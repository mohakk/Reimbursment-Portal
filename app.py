from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import re
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_config = {
    'user': 'root',
    'password': '7587061048@Mg',
    'host': 'localhost',
    'database': 'reimbursement_db'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    logging.info(f"Login attempt for user: {email}")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    
    if user:
        session['email'] = user['email']
        session['role'] = user['role']
        logging.info(f"Login successful for user: {email}") 
        if user['role'] == 'manager':
            return redirect(url_for('manager_dashboard'))
        elif user['role'] == 'employee':
            return redirect(url_for('employee_dashboard'))
        elif user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
    else:
        logging.warning(f"Login failed for user: {email}")
        return "Invalid email or password"

@app.route('/logout')
def logout():
    email = session['email']
    session.pop('email', None)
    session.pop('role', None)

    logging.info(f"User {email} logged out")

    return render_template('login.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'email' not in session or 'role' not in session or session['role'] != 'manager':
        return redirect(url_for('index'))
    return render_template('manager_dashboard.html')

@app.route('/employee_dashboard')
def employee_dashboard():
    if 'email' not in session or 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('index'))
    return render_template('employee_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'email' not in session or 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')


# Admin Functionalities------------------------------------------

@app.route('/view_users')
def view_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT users.email, users.password, users.role, users.department_name 
        FROM users WHERE users.department_name IS NOT NULL
    """)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        admin_email = session['email']
        email = request.form['email']
        password = request.form['password']
        department_name = request.form['department_name']
        role = request.form['role']

        if not re.match(r".*@example\.com$", email):
         logging.warning(f"User addition by {admin_email} failed due to inappropriate credentials")
         flash('Email must end with @example.com', 'error')
         return redirect(url_for('add_user'))

        logging.info(f"{admin_email} added a {role} with email:{email} to the {department_name} department")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (email, password, department_name, role)
            VALUES (%s, %s, %s, %s)
        """, (email, password, department_name, role))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('view_users'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM departments")
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('add_user.html', departments=departments)

@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        admin_email = session['email']
        email = request.form['email']
        
        logging.info(f"{admin_email} deleted {email}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM users
            WHERE email=%s;
        """, (email,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('delete_user'))
    

    return render_template('delete_user.html')

@app.route('/view_departments')
def view_departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * from departments 
    """)
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_departments.html', departments=departments)

@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        admin_email = session['email']
        department_name = request.form['department_name']
        
        logging.info(f"{admin_email} added {department_name} department")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO departments (name)
            VALUES (%s)
        """, (department_name,))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('add_department'))
    
    return render_template('add_department.html')

@app.route('/delete_department', methods=['GET', 'POST'])
def delete_department():
    if request.method == 'POST':
        admin_email = session['email']
        department = request.form['name']

        logging.info(f"{admin_email} deleted {department} department")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM departments
            WHERE name=%s;
        """, (department,))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('delete_department'))
    

    return render_template('delete_department.html')



# Manager Functionalities------------------------------------------

@app.route('/view_requests')
def view_requests():
    if 'email' not in session:
        return redirect(url_for('login'))

    manager_email = session['email']
    pending = 'pending'
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    cursor.execute("SELECT department_name FROM users WHERE email = %s", (manager_email,))
    manager_department = cursor.fetchone()['department_name']
    
    cursor.execute("""
        SELECT rr.*
        FROM reimbursement_requests rr
        JOIN users u ON rr.email = u.email
        WHERE u.department_name = %s AND status = %s
    """, (manager_department, pending))
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_requests.html', requests=requests)

@app.route('/update_request', methods=['POST'])
def update_request():
    manager_email = session['email']
    req_id = request.form['id']
    status = request.form['status']
    comment = request.form['comment']

    logging.info(f"{manager_email} {status} reimbursement request with id: {req_id}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reimbursement_requests
        SET status = %s, comment = %s
        WHERE id = %s
    """, (status, comment, req_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('view_requests'))

@app.route('/view_processed_requests')
def view_processed_requests():
    manager_email = session['email']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT department_name FROM users WHERE email = %s", (manager_email,))
    manager_department = cursor.fetchone()['department_name']
    
    cursor.execute("""
        SELECT rr.*
        FROM reimbursement_requests rr
        JOIN users u ON rr.email = u.email
        WHERE u.department_name = %s AND status IN ('approved', 'rejected', 'on hold')
    """, (manager_department,))
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_processed_requests.html', requests=requests)



# Employee Funnctionalities----------------------------------------------
@app.route('/claim_reimbursement_form')
def claim_reimbursement_form():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('claim_reimbursement_form.html')
    

@app.route('/claim_reimbursement', methods=['POST'])
def claim_reimbursement():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email'] 
    expense_type = request.form['expense_type']
    amount = request.form['amount']
    date = request.form['date']
    
    logging.info(f"{email} has claimed a reimbursement request")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reimbursement_requests (email, expense_type, amount, date, status, comment) VALUES (%s, %s, %s, %s, %s, %s)",
        (email, expense_type, amount, date, 'pending', '')
    )
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('claim_confirmation.html')


@app.route('/view_requests_employee')
def view_requests_employee():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']  
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM reimbursement_requests WHERE email = %s", (email,))
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_requests_employee.html', requests=requests)



if __name__ == '__main__':
    app.run(debug=True)
