from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import Config
import bcrypt
import random

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
            return redirect(url_for('dashboard'))
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
    
    filter_type = request.args.get('filter_by', 'all')

    cursor = mysql.connection.cursor()

    #Get User Profile 
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

    #Get Filtered Transactions
    if filter_type == 'income':
        cursor.execute("""
            SELECT t.TransactionID, t.Type, t.Amount, t.Date, t.Source, t.Description, l.Name AS Label
            FROM Transactions t
            LEFT JOIN Labels l ON t.LabelID = l.LabelID
            WHERE t.UserID = %s AND t.Type = 'income'
            ORDER BY t.Date DESC, t.TransactionID DESC
        """, [session['UserID']])
    elif filter_type == 'expense':
        cursor.execute("""
            SELECT t.TransactionID, t.Type, t.Amount, t.Date, t.Source, t.Description, l.Name AS Label
            FROM Transactions t
            LEFT JOIN Labels l ON t.LabelID = l.LabelID
            WHERE t.UserID = %s AND t.Type = 'expense'
            ORDER BY t.Date DESC, t.TransactionID DESC
        """, [session['UserID']])
    else:
        cursor.execute("""
            SELECT t.TransactionID, t.Type, t.Amount, t.Date, t.Source, t.Description, l.Name AS Label
            FROM Transactions t
            LEFT JOIN Labels l ON t.LabelID = l.LabelID
            WHERE t.UserID = %s
            ORDER BY t.Date DESC, t.TransactionID DESC
        """, [session['UserID']])

    transactions = cursor.fetchall()
    cursor.close()

    #Implementation of Tips on the Dashboard
    Financial_Tips = [
        "Save at least 20% of your income each month before spending.",
        "Track every expense, no matter how small — small purchases add up quickly.",
        "Build an emergency fund that covers at least 3 months of expenses.",
        "Avoid spending money you haven't earned yet — live within your means.",
        "Review your spending habits at the end of each month to identify patterns.",
        "Pay yourself first — set aside savings before paying any other bills.",
        "Avoid impulse purchases by waiting 24 hours before buying non-essentials.",
        "Use labels to categorise your spending so you can see where your money goes.",
        "Set a monthly spending limit and stick to it — every dollar counts.",
        "Financial freedom starts with small consistent habits, not big one-time changes."
    ]

    tips = random.sample(Financial_Tips, 3)

    return render_template('dashboard.html', user=user, balance=balance, latest_transaction=latest_transaction, transactions=transactions, filter_type=filter_type, tips=tips)

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

#Edit Transaction Route
@app.route('/edittransaction/<int:transaction_id>', methods=['GET', 'POST'])
def edittransaction(transaction_id):
    if 'UserID' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()

    #Gets the transaction ot be edited 
    cursor.execute("SELECT * FROM Transactions WHERE TransactionID = %s AND UserID = %s", (transaction_id, session['UserID']))
    transaction = cursor.fetchone()

    if not transaction:
        flash('Transaction not found.', 'error')
        return redirect(url_for('dashboard'))

    #Gets the labels for the dropdown menu
    cursor.execute("SELECT LabelID, Name FROM Labels WHERE UserID = %s", [session['UserID']])
    labels = cursor.fetchall()

    if request.method == 'POST':
        amount = request.form['amount']
        date = request.form['date']
        source = request.form['source']
        description = request.form['description']
        label_id = request.form['label_id'] or None

        try:
            cursor.execute("""
                UPDATE Transactions 
                SET Amount = %s, Date = %s, Source = %s, Description = %s, LabelID = %s
                WHERE TransactionID = %s AND UserID = %s
            """, (amount, date, source, description, label_id, transaction_id, session['UserID']))
            mysql.connection.commit()
            flash('Transaction updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Error updating transaction. Please try again.', 'danger')
        finally:
            cursor.close()

    cursor.close()
    return render_template('edittransaction.html', transaction=transaction, labels=labels)

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
            flash('Error creating label.', 'error')

    #Gets all labels for this user
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT LabelID, Name FROM Labels WHERE UserID = %s", [session['UserID']])
    labels = cursor.fetchall()
    cursor.close()

    return render_template('labels.html', labels=labels)

#Delete Label Route
@app.route('/deletelabel/<int:label_id>')
def deletelabel(label_id):
    if 'UserID' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Labels WHERE LabelID = %s AND UserID = %s",
                (label_id, session['UserID']))
    mysql.connection.commit()
    cursor.close()
    flash('Label deleted successfully!', 'success')
    return redirect(url_for('labels'))

#Run
if __name__ == '__main__':
    app.run(debug=True)
