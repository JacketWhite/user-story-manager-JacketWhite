from flask import Flask, request, session, g, redirect, url_for, abort, flash, render_template
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'ss'
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'user_stories.db'),
))
app.config.from_envvar('USM_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('user_stories.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
@app.route('/list')
def list():
    db = get_db()
    cur = db.execute('select * from user_stories order by ID asc')
    entries = cur.fetchall()
    return render_template('list.html', entries=entries)


@app.route('/story/submit', methods=['POST'])
def story():
    db = get_db()
    db.execute("""insert into user_stories (Story_Title, User_Story, Acceptance_Criteria, Business_Value, Estimation, Status)
               values (?, ?, ?, ?, ?, ?)""",
               [request.form['Story_Title'],
                request.form['User_Story'],
                request.form['Acceptance_Criteria'],
                request.form['Business_Value'],
                request.form['Estimation'],
                request.form['Status']])
    db.commit()
    flash('New story was succesfully added')
    return redirect(url_for('list'))


@app.route('/story', methods=['GET'])
def get_form():
    entry = []
    return render_template('form.html', entry=entry)


@app.route('/delete/<id>', methods=['POST'])
def delete_story(id):
    db = get_db()
    db.execute("""DELETE from user_stories where ID=?""", [id])
    db.commit()
    return redirect(url_for('list'))


@app.route('/update/<id>', methods=['POST'])
def update_story(id):
    db = get_db()
    db.execute("""UPDATE user_stories SET
               Story_Title=?, User_Story=?, Acceptance_Criteria=?, Business_Value=?, Estimation=?, Status=? WHERE id=?""",
               [request.form['Story_Title'], request.form['User_Story'],
                request.form['Acceptance_Criteria'], request.form['Business_Value'],
                request.form['Estimation'], request.form['Status'], [id]])
    db.commit()
    return redirect(url_for('list'))


@app.route('/story/<id>', methods=['GET'])
def filled_form(id):
    db = get_db()
    story = fetch_data(id, db)
    return render_template('form.html', route='update_story', methods=['POST'], id=id, user_story=story)


def fetch_data(id, db):
    titles = ('Story_Title', 'User_Story', 'Acceptance_Criteria',
              'Business_Value', 'Estimation', 'Status')
    user_story = {}
    cur = db.execute("""SELECT Story_Title, User_Story, Acceptance_Criteria,
                  Business_Value, Estimation, Status FROM user_stories WHERE ID=?""", [id])
    try:
        story = cur.fetchall()[0]
        for i, title in enumerate(titles):
            print(story[i], title)
            user_story[title] = story[i]
        return user_story
    except IndexError:
        return user_story
