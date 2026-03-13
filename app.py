from flask import Flask
from flask_mysqldb import MySQL
from flask_session import Session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

#Route 
@app.route('/')
def index():
    return 'Budgeting System is running!'

#Run
if __name__ == '__main__':
    app.run(debug=True)
