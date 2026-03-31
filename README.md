# Budgeting-System
Software Engineering Final Project

## System Architecture 
Frontend: HTML, CSS, JS 

Backend: Python with Flask 

Database: MySQL 

## Project Tool Documentation 
Flask is used as the Web Framework.

Regarding Flask, MySQL and bcrypt Documentation please use the link below:

https://flask.palletsprojects.com/en/stable/quickstart/

https://flask.palletsprojects.com/en/stable/quickstart/#sessions

https://flask.palletsprojects.com/en/stable/patterns/flashing/

https://flask-mysql.readthedocs.io/en/stable/#configuration

https://pypi.org/project/bcrypt/

https://jinja.palletsprojects.com/en/3.1.x/templates/

Also see the below screenshots:
[Flask Documentation](images/flask_docs.png)

This also outlines some code that was used in the inital app.py code.

## Database
With the use of MySQL the database creation has begun. The database name is budgeting_system. 

Through the initial creation of the database, the below tables have been implemented accordingly:
    
    - Users
    
    - Labels 
    
    - Transactions 
    
    - Budget
    
    - Alerts
    
    - Reports

## Error Fixes
Please see the below screenshots related to the user_id error:

Caused due to user_id mismatch between code was rectified to UserID officially.
[user_id Error Documentation](images/user_id%20error.png)

[user_id Error Extended Documentation](images/user_id%20error%20extended.png)

This is due to a error of not initialize cursor, I did cursor.mysql.connection.cursor() instead of cursor = mysql.connection.cursor()
[cursor implementation Error Documentation](images/Cursor%20coding%20Error.png)

This is due to me not placing the EditTransaction.html file into the templates folder, so flask was unable to find it
[EditTransaction Error Documentation](images/EditTransaction.html%20Error.png)

## Documentation Milestones
Successfully implemented the addition of transactions for each user.

[Tranaction Implementaiton Documentaiton](images/Adding%20Transaction%20Success.png)

[Adding Transactions Dropdown Documentation](images/Add%20Transaction%20Dropdown%20Menu.png)

[Fixed Transaction History All Display Documentation](images/All%20Transaction%20History%20Tab.png)

[Fixed Transaction History Income Display Documentation](images/Income%20Transaction%20History%20Tab.png)

[Fixed Transaction History Expense Display Documentation](images/Expense%20Transaction%20History%20Tab.png)

[Added Limited Editing to Transactions Documentation](images/Added%20Edit%20Button.png)

[Edit Transaction Menu Documentation](images/Edit%20Transaction%20Menu.png)





