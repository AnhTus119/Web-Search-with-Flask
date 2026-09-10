from flask import Blueprint, render_template, request, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('search.search'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'Anh Tú' and password == '12345':
            session['username'] = username
            return redirect(url_for('search.search'))

        message = 'Invalid username or password'

    return render_template('Login.html', message=message)

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
