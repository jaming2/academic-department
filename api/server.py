from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')
db_path = os.path.join(BASE_DIR, 'users.db')

# 서버 시작 시 기존 DB 삭제
if os.path.exists(db_path):
    os.remove(db_path)

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

app.secret_key = 'secret_key'

# 새 DB 생성
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()


@app.route('/')
def main_page():
    username = session.get('username')
    return render_template('main.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login_page():

    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['username'] = username
            return redirect('/')
        else:
            error = '아이디 또는 비밀번호가 틀렸습니다.'

    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():

    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )

            conn.commit()
            conn.close()

            return redirect('/login')

        except:
            error = '이미 존재하는 아이디입니다.'

    return render_template('signup.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/1st_python_study')
def python_study_page():
    return render_template('study.html')


if __name__ == '__main__':
    app.run(debug=True)