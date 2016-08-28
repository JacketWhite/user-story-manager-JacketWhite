from flask import Flask, request, session, g, redirect, url_for, abort, flash, render_template
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'user_stories.db')
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
def show_entries():
    db = get_db()
    cur = db.execute('select ID, Story_Title, User_Story, Acceptance_Criteria, Business_Value, Estimation, Status from user_stories order by ID desc')
    entries = cur.fetchall
    return render_template('index.html', entries=entries)

@app.route('/story')
def story():
    return render_template('index.html')
