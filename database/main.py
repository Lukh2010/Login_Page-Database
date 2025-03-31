from flask import Flask, redirect, render_template, request
import json
import os

app = Flask(__name__)
# File to store user data
USER_LOG_FILE = 'user_log.txt'

# Function to log user data
def log_user(username, password):
    with open(USER_LOG_FILE, 'a') as f:
        f.write(f"{username},{password}\n")  # Log format: username,password

# Function to load users from the log file
def load_users():
    users = []
    try:
        with open(USER_LOG_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:  # Ensure there are exactly two parts
                    username, password = parts
                    users.append({'username': username, 'password': password})
                else:
                    print(f"Malformed line: {line.strip()}")  # Log malformed lines for debugging
    except FileNotFoundError:
        pass  # If the file doesn't exist, return an empty list
    return users
@app.route('/user-output', methods=['GET', 'POST'])
def user_output():
    if request.method == 'POST':
        username = request.form['username']   # Get the username and password from the form
        password = request.form['password']
        
        users = load_users()  # Load existing users
        
        # Check if user already exists
        for user in users:
            if user['username'] == username:
                return render_template('register.html', output="Username already exists.")  # Show error message
        
        log_user(username, password)  # Log the new user
        return render_template('register.html', output="Registered successfully!")  # Show success message
    
    return render_template('register.html')

@app.route('/list-users')
def list_users():
    users = load_users()  # Load users from the log file
    return render_template('list_users.html', users=users)  # Pass users to the template

@app.route('/register')
def register():
    """Render the registration page."""
    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/registered')
def registered():
    return render_template('registered.html')