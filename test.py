from flask import Flask, render_template, request, redirect, session
import mysql.connector, random

app = Flask(__name__)

# For Datavase
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "atm_67_b"

# For Session
app.config['SECRET_KEY'] ="dghgdmshosdghkodsngohnodkgnokodkgnkng"

# random account_number
def generate_account_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])
@app.route('/register', methods=['GET', 'POST'])
def register():
    account_number = generate_account_number() if request.method == 'GET' else request.form.get('account_number')
    return render_template('register.html', account_number=account_number)


@app.route("/create", methods=["POST"])
def create():
    if request.method == "POST":
        account_number = request.form['account_number']
        username = request.form['username']
        balance = request.form['balance']
        print ("Input:",account_number,username,balance)
        
        # Connect to Database
        my_db = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASS,
            db = DB_NAME,
        )
        my_cursor = my_db.cursor(dictionary=True)
        sql = "INSERT INTO atm_member(account_number, username, balance) VALUES (%s,%s,%s)"
        val = (account_number,username,balance)
        my_cursor.execute(sql, val)
        my_db.commit()
        return redirect("/")
    
        
    #     session['alert_status'] = "success"
    #     session['alert_message'] = "Already Created!"
    #     return redirect("/")
        
    # else:
    #     session['alert_status'] = "fail"
    #     session['alert_message'] = "Something went wrong!"
    #     return redirect("/")
    
@app.route("/")
def index():
    # Show Messages
    if "alert_status" in session and "alert_message" in session:
        alert_message = {
            'status': session["alert_status"],
            'message': session["alert_message"],
        }
        del session["alert_status"]
        del session["alert_message"]
    
    else:
        alert_message = {
            'status': None,
            'message': None,
        }
        
    
    return render_template("index.html",alert_message = alert_message)


@app.route("/show", methods=['GET', 'POST'])
def show():
    if request.method == "POST":
        username = request.form['username']
        print("Input:", username)
        
        # Connect to Database
        my_db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        
        my_cursor = my_db.cursor(dictionary=True)
        sql = "SELECT * FROM atm_member WHERE username = %s"
        val = (username,)
        my_cursor.execute(sql, val)
        results = my_cursor.fetchall()
        
        # เก็บ session username
        if results:
            session['username'] = username
            session['alert_status'] = "success"
            session['alert_message'] = "Login successful!"
        else:
            session['username'] = ""
            session['alert_status'] = "fail"
            session['alert_message'] = "Something went wrong!"
            return redirect("/")
        
        # Use redirect to avoid form re-submission on refresh
        return redirect("/show")

    # Handle GET request
    else:
        username = session.get('username')

        # Connect to Database
        my_db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        
        my_cursor = my_db.cursor(dictionary=True)
        sql = "SELECT * FROM atm_member WHERE username = %s"
        val = (username,)
        my_cursor.execute(sql, val)
        results = my_cursor.fetchall()
        
        # Show Messages
        if "alert_status" in session and "alert_message" in session:
            alert_message = {
                'status': session["alert_status"],
                'message': session["alert_message"],
            }
            del session["alert_status"]
            del session["alert_message"]
        else:
            alert_message = {
                'status': None,
                'message': None,
            }
            
        return render_template("show.html", alert_message=alert_message, results=results, username=username)

    
@app.route("/deposit/<user_id>" , methods=['GET'])
def deposit(user_id):
    # Conect Database
    my_db = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASS,
            db = DB_NAME
        )
    my_cursor = my_db.cursor(dictionary=True)
    sql = "SELECT * FROM atm_member WHERE id = " + user_id
    my_cursor.execute(sql)
    results = my_cursor.fetchone()

    return render_template("deposit.html", results = results)

@app.route("/update_deposit/<user_id>" , methods=["POST"])
def update_deposit(user_id):
    # Conect Database
    my_db = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASS,
            db = DB_NAME
        )
    my_cursor = my_db.cursor(dictionary=True)
    sql = "SELECT * FROM atm_member WHERE id = " + user_id
    my_cursor.execute(sql)
    results = my_cursor.fetchone()
    
    if request.method == 'POST':
        balance = float(request.form['balance'])
    current_balance = results.get('balance', 0.0)
    new_balance = current_balance + balance
        
    sql = "UPDATE atm_member SET balance = %s WHERE id = %s"
    val = (new_balance, user_id)
    my_cursor.execute(sql, val)
    my_db.commit()
    session['alert_status'] = "success"
    session['alert_message'] = "Deposit successful!"
    return redirect('/show')


@app.route("/withdraw/<user_id>" , methods=['GET'])
def withdraw(user_id):
    # Conect Database
    my_db = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASS,
            db = DB_NAME
        )
    my_cursor = my_db.cursor(dictionary=True)
    sql = "SELECT * FROM atm_member WHERE id = " + user_id
    my_cursor.execute(sql)
    results = my_cursor.fetchone()

    return render_template("withdraw.html", results = results)

@app.route("/update_withdraw/<user_id>", methods=["POST"])
def update_withdraw(user_id):
    # Connect Database
    my_db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    my_cursor = my_db.cursor(dictionary=True)
    sql = "SELECT * FROM atm_member WHERE id = %s"
    val = (user_id,)
    my_cursor.execute(sql, val)
    results = my_cursor.fetchone()

    if not results:
        # Handle the case where the user doesn't exist
        session['alert_status'] = "fail"
        session['alert_message'] = "User not found!"
        return redirect('/show')

    if request.method == 'POST':
        balance = float(request.form['balance'])
    current_balance = results.get('balance', 0.0)
    new_balance = current_balance - balance

    if new_balance < 0:
        new_balance = current_balance
        session['alert_status'] = "fail"
        session['alert_message'] = "Not enough money!"
    else:
        sql = "UPDATE atm_member SET balance = %s WHERE id = %s"
        val = (new_balance, user_id)
        my_cursor.execute(sql, val)
        my_db.commit()
        session['alert_status'] = "success"
        session['alert_message'] = "Withdrawal successful!"
    return redirect('/show')


@app.route('/leave')
def leave():
    del session['username']
    return redirect("/")

@app.route('/delete', methods=['GET'])
def delete_confirmation():
    return render_template('confirmation.html')

@app.route("/delete/<user_id>", methods=["GET"])
def delete(user_id):
    # Connect to Database
        my_db = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASS,
            db = DB_NAME,
        )
        my_cursor = my_db.cursor(dictionary=True)
        sql = "DELETE FROM atm_67_b WHERE id = " + user_id
        my_cursor.execute(sql)
        my_db.commit()
        del session['username']
        
        session['alert_status'] = "success"
        session['alert_message'] = "Already Deleted!"
        return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)