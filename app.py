from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import Config
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

#Home Route
@app.route('/')
def index():
    return redirect(url_for('login'))

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
            session['UserID'] = user['UserID']
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
def dashboard():
    if 'UserID' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()

    #Retrieve User Profiles 
    cursor.execute("SELECT Username FROM Users WHERE UserID = %s", [session['UserID']])
    user = cursor.fetchone()

    #Obtain User's Current Balance
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN Type = 'income' THEN Amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN Type = 'expense' THEN Amount ELSE 0 END), 0) 
        AS Balance
        FROM Transactions 
        WHERE UserID = %s
    """, [session['UserID']])
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

#Transaction Route
@app.route('/transaction', methods=['GET', 'POST'])
def addtransaction():
    if 'UserID' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    #Get the labels for the dropdown menu
    cursor.execute("SELECT LabelID, Name FROM Labels WHERE UserID = %s", [session['UserID']])
    labels = cursor.fetchall()

    #Gets the required data from the database
    if request.method == 'POST':
        transaction_type = request.form['type']
        amount = request.form['amount']
        date = request.form['date']
        source = request.form['source']
        description = request.form['description']
        label_id = request.form['label_id'] or None

        try:
            cursor.execute("""
                INSERT INTO Transactions (UserID, Type, Amount, Date, Source, Description, LabelID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (session['UserID'], transaction_type, amount, date, source, description, label_id))
            mysql.connection.commit()
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Error adding transaction. Please try again.')
        finally:
            cursor.close()

    cursor.close()
    return render_template('addtransaction.html', labels=labels)

#Label Management Route
@app.route('/labels', methods=['GET', 'POST'])
def labels():
    if 'UserID' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        try:
            cur.execute("INSERT INTO Labels (UserID, Name) VALUES (%s, %s)",
                        (session['UserID'], name))
            mysql.connection.commit()
            flash('Label created successfully!', 'success')
        except Exception as e:
            flash('Error creating label.', 'danger')

    #Gets all labels for this user
    cur.execute("SELECT LabelID, Name FROM Labels WHERE UserID = %s", [session['UserID']])
    labels = cur.fetchall()
    cur.close()

    return render_template('labels.html', labels=labels)


@app.route('/deletelabel/<int:label_id>')
def deletelabel(label_id):
    if 'UserID' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Labels WHERE LabelID = %s AND UserID = %s",
                (label_id, session['UserID']))
    mysql.connection.commit()
    cur.close()
    flash('Label deleted successfully!', 'success')
    return redirect(url_for('labels'))

#Run
if __name__ == '__main__':
    app.run(debug=True)
