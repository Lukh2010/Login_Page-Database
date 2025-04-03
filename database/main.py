from flask import Flask, redirect, render_template, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = '06387318de54018d05f792a76c9ef93fb1d712e13f51e19c'

# Where to store user data
USER_LOG_FILE = 'database/user_log.txt'

# Function to save user data
def log_user(username, password, name, address, birthdate, role='normal'):
    try:
        datetime.strptime(birthdate, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid birthdate format: {birthdate}")
        return

    with open(USER_LOG_FILE, 'a') as f:
        f.write(f"{username},{password},{name},{address},{birthdate},{role}\n")

# Load all the information from the log file
def load_users():
    users = []
    try:
        with open(USER_LOG_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 6:
                    username, password, name, address, birthdate, role = parts
                    try:
                        birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
                        age = (datetime.now() - birthdate).days // 365
                        users.append({'username': username, 'password': password, 'name': name, 'address': address, 'birthdate': birthdate.strftime('%Y-%m-%d'), 'age': age, 'role': role})
                    except ValueError:
                        print(f"Invalid birthdate format: {birthdate}")
                else:
                    print(f"Malformed line: {line.strip()}")
    except FileNotFoundError:
        pass
    return users

@app.route('/')
def home():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect('/list-users')

    if request.method == 'POST':
        username = request.form['username']      # get the informations
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        birthdate = request.form['birthdate']

        try:
            birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d')
            if birthdate_obj > datetime.now():
                return render_template('register.html', output="Birthdate cannot be in the future.")   # calculate the age
        except ValueError:
            return render_template('register.html', output="Invalid birthdate format.")

        users = load_users()
        for user in users:
            if user['username'] == username:
                return render_template('register.html', output="Username already exists.")  # check if user exists

        log_user(username, password, name, address, birthdate)  # Log the new user
        session['logged_in'] = True
        return redirect('/list-users')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect('/list-users')

    if request.method == 'POST':
        username = request.form['username']   
        password = request.form['password']
        
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:  # check login data
                session['logged_in'] = True
                session['role'] = user['role']
                return redirect('/list-users')
        
        return render_template('login.html', output="Invalid username or password.")

    return render_template('login.html')

@app.route('/list-users', methods=['GET', 'POST'])
def list_users():
    if 'logged_in' not in session:
        return redirect('/register')

    if request.method == 'POST':
        key = request.form.get('key')
        users = load_users()
        if key == 'Vp2dykzmTD9/q8BzwItVAPZH1cCdWZnsOPDZDdbMHK8=':
            return render_template('list_users.html', users=users, show_sensitive=True)   # check for the key
        else:
            return render_template('list_users.html', users=users, show_sensitive=False)

    users = load_users()
    return render_template('list_users.html', users=users, show_sensitive=False)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)   # logout button
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)   # on what port its running