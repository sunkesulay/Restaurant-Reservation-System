from flask import Flask, render_template, request, redirect, url_for,session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'restreserve'  

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'restreserve'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_reservations')
def view_reservations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reservations")
    columns = [column[0] for column in cur.description]
    reservations = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()

    print(reservations)  # Add this line for debugging

    return render_template('viewReservations.html', reservations=reservations)


@app.route('/reserve')
def reserve():
    cur = mysql.connection.cursor()
    cur.execute("SELECT table_id, capacity, is_booked FROM tables")
    columns = [column[0] for column in cur.description]
    tables = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()

    return render_template('reserve.html', tables=tables)



@app.route('/book_table/<int:table_id>', methods=['GET', 'POST'])
def book_table(table_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        guest_name = request.form['guest_name']
        guest_phone = request.form['guest_phone']
        guest_email = request.form['guest_email']
        reservation_date = request.form['reservation_date']
        reservation_time = request.form['reservation_time']
        num_of_guests = request.form['num_of_guests']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO reservations (user_id, table_id, reservation_date, reservation_time, num_of_guests, is_guest_user)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, table_id, reservation_date, reservation_time, num_of_guests, 1))

        cur.execute("UPDATE tables SET is_booked = 1 WHERE table_id = %s", (table_id,))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('reserve'))

    return render_template('book_table.html', table_id=table_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_phone = request.form['emailPhone']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM users WHERE (email = %s OR phone = %s) AND password_hash = %s", (email_phone, email_phone, password))
        user_id_tuple = cur.fetchone()
        cur.close()

        if user_id_tuple:
            user_id = user_id_tuple[0]

            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        else:
            # Login failed, redirect back to login page
            return redirect(url_for('login'))

    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        mailing_address = request.form['mailing_address']
        billing_address = request.form['billing_address']
        preferred_payment_method = request.form['preferred_payment_method']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (name, email, phone, mailing_address, billing_address, preferred_payment_method, password_hash) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, email, phone, mailing_address, billing_address, preferred_payment_method, password)
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/add_table', methods=['GET', 'POST'])
def add_table():
    if request.method == 'POST':
        capacity = int(request.form['capacity'])
        is_combinable = int(request.form['is_combinable'])

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tables (capacity, is_combinable) VALUES (%s, %s)", (capacity, is_combinable))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('add_table'))

    return render_template('add_table.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))




@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']

        if admin_id == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('admin_login'))

    return render_template('adminLogin.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('admin_logged_in'):
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))



if __name__ == '__main__':
    app.run(debug=True)
