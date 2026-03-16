from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import Config
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

#Register Route 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        password = request.form['password']

        #Password hashing
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        #Database insertion
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO Users (Username, Email, Password_Hash) VALUES (%s, %s, %s)", (username, email, password_hash))
            mysql.connection.commit()
            flash('Account Created Successfully! Please log In.', 'Success')
            return redirect(url_for('login'))
        except:
            flash('Username or Email already exists.', 'Error')
        finally:
            cursor.close()
    
    return render_template('register.html')

#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = %s", [username])
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['Password_Hash'].encode('utf-8')):
            session['user_id'] = user['UserID']
            session['Username'] = user['Username']
            flash('Logged in successfully!', 'Success')
            return redirect(url_for('Dashboard'))
        else:
            flash("Invalid username or password.", 'Error')
    
    return render_template('login.html')

#Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'Success')
    return redirect(url_for('login'))

#Dashboard Route
@app.route('/dashboard')
def Dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()

    #Retrieve User Profiles 
    cursor.execute("SELECT Username FROM Users WHERE UserID = %s", [session['user_id']])
    user = cursor.fetchone()

    #Obtain User's Current Balance
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN Type = 'income' THEN Amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN Type = 'expense' THEN Amount ELSE 0 END), 0) 
        AS Balance
        FROM Transactions 
        WHERE UserID = %s
    """, [session['user_id']])
    balance = cursor.fetchone()

    #Obtain The Latest Transaction
    cursor.execute("""
        SELECT Type, Amount, Date, Description 
        FROM Transactions 
        WHERE UserID = %s 
        ORDER BY Date DESC
        LIMIT 1
    """, [session['UserID']])
    latest_transaction = cursor.fetchone()

    cursor.close()

    return render_template('dashboard.html', user=user, balance=balance, latest_transaction=latest_transaction)

#Run
if __name__ == '__main__':
    app.run(debug=True)
