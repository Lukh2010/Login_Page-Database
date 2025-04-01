from flask import Flask, redirect, render_template, request, session  # Import session
import json
import os
from datetime import datetime  # Import datetime for age calculation

app = Flask(__name__)
app.secret_key = '06387318de54018d05f792a76c9ef93fb1d712e13f51e19c'  # Session secret key

# File to store user data
USER_LOG_FILE = 'user_log.txt'

# Function to log user data
def log_user(username, password, name, address, birthdate):
    # Validate birthdate format
    try:
        datetime.strptime(birthdate, '%Y-%m-%d')  # Ensure the birthdate is in the correct format
    except ValueError:
        print(f"Invalid birthdate format: {birthdate}")  # Log invalid format
        return  # Exit the function if the format is invalid

    with open(USER_LOG_FILE, 'a') as f:
        f.write(f"{username},{password},{name},{address},{birthdate}\n")  # Log format: username,password,name,address,birthdate

# Function to load users from the log file
def load_users():
    users = []
    try:
        with open(USER_LOG_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 5:  # Ensure there are exactly five parts
                    username, password, name, address, birthdate = parts
                    # Validate birthdate format
                    try:
                        birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
                        age = (datetime.now() - birthdate).days // 365
                        users.append({'username': username, 'password': password, 'name': name, 'address': address, 'birthdate': birthdate.strftime('%Y-%m-%d'), 'age': age})
                    except ValueError:
                        print(f"Invalid birthdate format: {birthdate}")  # Log invalid format
                else:
                    print(f"Malformed line: {line.strip()}")  # Log malformed lines for debugging
    except FileNotFoundError:
        pass  # If the file doesn't exist, return an empty list
    return users

@app.route('/')
def home():
    return redirect('/register')  # Redirect to the registration page

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Render the registration page and handle registration logic."""
    if 'logged_in' in session:  # Check if user is already logged in
        return redirect('/list-users')  # Redirect to the list-users page if logged in

    if request.method == 'POST':
        username = request.form['username']   # Get the username and password from the form
        password = request.form['password']  # Get the password
        name = request.form['name']  # Get the name
        address = request.form['address']  # Get the address
        birthdate = request.form['birthdate']  # Get the birthdate
        
        # Validate birthdate
        try:
            birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d')
            if birthdate_obj > datetime.now():
                return render_template('register.html', output="Birthdate cannot be in the future.")  # Show error message
        except ValueError:
            return render_template('register.html', output="Invalid birthdate format.")  # Show error message

        users = load_users()  # Load existing users
        
        # Check if user already exists
        for user in users:
            if user['username'] == username:
                return render_template('register.html', output="Username already exists.")  # Show error message
        
        log_user(username, password, name, address, birthdate)  # Log the new user
        session['logged_in'] = True  # Set session variable to indicate user is logged in
        return redirect('/list-users')  # Redirect to the list-users page

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Render the login page and handle login logic."""
    if 'logged_in' in session:  # Check if user is already logged in
        return redirect('/list-users')  # Redirect to the list-users page if logged in

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()  # Load existing users
        
        # Check if the username and password match
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['logged_in'] = True  # Set session variable to indicate user is logged in
                return redirect('/list-users')  # Redirect to the list-users page
        
        return render_template('login.html', output="Invalid username or password.")  # Show error message

    return render_template('login.html')

@app.route('/list-users')
def list_users():
    if 'logged_in' not in session:  # Check if user is logged in
        return redirect('/register')  # Redirect to registration page if not logged in
    users = load_users()  # Load users from the log file
    return render_template('list_users.html', users=users)  # Pass users to the template

@app.route('/logout')
def logout():
    """Log the user out and redirect to the login page."""
    session.pop('logged_in', None)  # Remove the logged-in session variable
    return redirect('/login')  # Redirect to the login page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
