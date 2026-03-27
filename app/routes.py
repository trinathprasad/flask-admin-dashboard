from flask import Blueprint, render_template, session, redirect, url_for, request
from .db import get_db_connection

main = Blueprint('main', __name__)

@main.route('/', methods=['GET','POST'])
def login():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    error = None 

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user['username']
            return redirect(url_for('main.dashboard'))
        else:
            error = "Invalid Credential"

    return render_template('login.html', error=error)


@main.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM apiusers")
        data = cursor.fetchall()

        active = sum(1 for row in data if row['status']=='active')
        inactive = sum(1 for row in data if row['status']=='inactive')

        return render_template(
            'dashboard.html',
            user=session['user'],
            data=data,
            active=active,
            inactive=inactive
        )
    else:
        return redirect(url_for('main.login'))


@main.route('/add')
def add_user():
    return render_template('add.html')


@main.route('/insert', methods=['POST'])
def insert_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    name = request.form['name']
    email = request.form['email']
    status = request.form['status']

    cursor.execute("""
        INSERT INTO apiusers (name, email, status)
        VALUES (%s, %s, %s)
    """, (name, email, status))

    conn.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/edit/<int:id>')
def edit_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM apiusers WHERE id=%s", (id,))
    user = cursor.fetchone()

    return render_template('edit.html', user=user)


@main.route('/update/<int:id>', methods=['POST'])
def update_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    name = request.form['name']
    email = request.form['email']
    status = request.form['status']

    cursor.execute("""
        UPDATE apiusers 
        SET name=%s, email=%s, status=%s 
        WHERE id=%s
    """, (name, email, status, id))

    conn.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM apiusers WHERE id=%s", (id,))
    conn.commit()

    return redirect(url_for('main.dashboard'))


@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main.login'))