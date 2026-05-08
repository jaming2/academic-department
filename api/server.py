from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
import subprocess
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key')


# ✅ Supabase DATABASE_URL (네가 테스트 성공한 방식)
DATABASE_URL = os.getenv("DATABASE_URL")


# 🔥 DB 연결 함수 (중복 제거 핵심)
def get_conn():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


# =========================
# 초기 테이블 생성
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS solved_problems (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            study_name TEXT NOT NULL,
            problem_number INTEGER NOT NULL
        )
    """)

    # 기존 DB 자동 마이그레이션
    cur.execute("""
        ALTER TABLE solved_problems
        ADD COLUMN IF NOT EXISTS study_name TEXT DEFAULT '2학기_1차_파이썬_스터디'
    """)

    conn.commit()
    cur.close()
    conn.close()


init_db()


# =========================
# ROUTES
# =========================

@app.route('/')
def main_page():
    return render_template('main.html', username=session.get('username'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            'SELECT password FROM users WHERE username=%s',
            (username,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row and check_password_hash(row[0], password):
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
            conn = get_conn()
            cur = conn.cursor()

            cur.execute(
                'INSERT INTO users (username, password) VALUES (%s, %s)',
                (username, generate_password_hash(password))
            )

            conn.commit()

            cur.close()
            conn.close()

            return redirect('/login')

        except Exception as e:
            print(e)
            error = '이미 존재하는 아이디입니다.'

    return render_template('signup.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


CURRENT_STUDY = '2학기_1차_파이썬_스터디'

@app.route('/1st_python_study')
def python_study_page():
    if 'username' not in session:
        return redirect('/login')

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        'SELECT problem_number FROM solved_problems WHERE username=%s AND study_name=%s',
        (session['username'], CURRENT_STUDY)
    )

    solved = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template('study.html', solved=solved)


@app.route('/submit_code', methods=['POST'])
def submit_code():

    if 'username' not in session:
        return jsonify({'success': False})

    data = request.get_json()

    code = data.get('code', '')
    problem_number = str(data.get('problem_number'))

    judge_path = os.path.join(
        BASE_DIR,
        'api',
        'study_judges',
        CURRENT_STUDY,
        f'{problem_number}번문제'
    )

    try:

        testcase_numbers = []

        for filename in os.listdir(judge_path):

            if filename.endswith('_input.txt'):

                number = (
                    filename
                    .replace('testcase', '')
                    .replace('_input.txt', '')
                )

                testcase_numbers.append(number)

        testcase_numbers.sort(key=int)

        if not testcase_numbers:

            return jsonify({
                'success': False,
                'message': '테스트케이스가 존재하지 않습니다.'
            })

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as temp:

            temp.write(code)
            temp_path = temp.name

        all_correct = True

        for number in testcase_numbers:

            input_path = os.path.join(
                judge_path,
                f'testcase{number}_input.txt'
            )

            output_path = os.path.join(
                judge_path,
                f'testcase{number}_output.txt'
            )

            with open(input_path, 'r', encoding='utf-8') as f:
                test_input = f.read()

            with open(output_path, 'r', encoding='utf-8') as f:
                correct_answer = f.read().strip()

            result = subprocess.run(
                ['python', temp_path],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=3
            )

            user_output = result.stdout.strip()

            if user_output != correct_answer:
                all_correct = False
                break

        if all_correct:

            conn = get_conn()
            cur = conn.cursor()

            cur.execute(
                '''
                SELECT *
                FROM solved_problems
                WHERE username=%s
                AND study_name=%s
                AND problem_number=%s
                ''',
                (session['username'], CURRENT_STUDY, int(problem_number))
            )

            already = cur.fetchone()

            if not already:
                cur.execute(
                    '''
                    INSERT INTO solved_problems
                    (username, study_name, problem_number)
                    VALUES (%s, %s, %s)
                    ''',
                    (session['username'], CURRENT_STUDY, int(problem_number))
                )
                conn.commit()

            cur.close()
            conn.close()

            return jsonify({'success': True})

        return jsonify({'success': False})

    except Exception as e:
        print(e)
        return jsonify({'success': False})


if __name__ == '__main__':
    app.run(debug=True)