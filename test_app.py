import unittest
from app import app, get_db_connection
from unittest.mock import patch, MagicMock
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Mock data for testing
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"
TEST_INVALID_EMAIL = "invalid@email.com"
TEST_INVALID_PASSWORD = "wrongpassword"




class ReimbursementAppTest(unittest.TestCase):


    @patch('mysql.connector.connect')
    def test_successful_connection(self, mock_connect):
        mock_conn = mock_connect.return_value  # Mock the connection object
        connection = get_db_connection()

        db_config = {
        'user': 'root',
        'password': '7587061048@Mg',
        'host': 'localhost',
        'database': 'reimbursement_db'
        }

        self.assertEqual(connection, mock_conn)
        mock_connect.assert_called_once_with(**db_config)

    @patch('app.get_db_connection')
    def test_login_success(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = {
            "email": TEST_USER_EMAIL,
            "role": "manager"
        }

        with app.test_client() as client:
            response = client.post('/login', data=dict(
                email=TEST_USER_EMAIL,
                password=TEST_USER_PASSWORD
            ))

            self.assertEqual(response.status_code, 302)  
            self.assertEqual(response.location, url_for('manager_dashboard')) 



    @patch('app.get_db_connection')
    def test_login_invalid_credentials(self, mock_get_db_connection):
        mock_get_db_connection.return_value.cursor.return_value.fetchone.return_value = None

        with app.test_client() as client:
            response = client.post('/login', data=dict(
                email=TEST_INVALID_EMAIL,
                password=TEST_INVALID_PASSWORD
            ))

            self.assertEqual(response.data.decode('utf-8'), "Invalid email or password")



# Manager
    def test_manager_dashboard_route(self):
        with app.test_client() as client:  
            with client.session_transaction() as session:
                session['email'] = 'test@manager.com'
                session['role'] = 'manager'

            response = client.get('/manager_dashboard')

            self.assertEqual(response.status_code, 200)

    def test_manager_dashboard_route_invalid_user(self):  
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'test@user.com'
                session['role'] = 'employee'  # Not a manager

            response = client.get('/manager_dashboard')

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('index'))



# Employee
    def test_employee_dashboard_route_authorized_employee(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'test@employee.com'
                session['role'] = 'employee'

            response = client.get('/employee_dashboard')

            self.assertEqual(response.status_code, 200)

    def test_employee_dashboard_route_unauthorized_user(self): 
        with app.test_client() as client:
            response = client.get('/employee_dashboard')

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('index'))

    def test_employee_dashboard_route_missing_session_data(self): 
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'test@user.com'  # Missing role

            response = client.get('/employee_dashboard')
    
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('index'))


# Admin
    def test_admin_dashboard_route_authorized_admin(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'test@admin.com'
                session['role'] = 'admin'

            response = client.get('/admin_dashboard')

            self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_route_unauthorized_user(self):
        with app.test_client() as client:
            response = client.get('/admin_dashboard')

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('index'))
    


    @patch('app.get_db_connection')
    def test_add_user_success(self, mock_get_db_connection):    
        mock_conn = mock_get_db_connection.return_value
        with app.test_client() as client:
            data = {
                'email': 'test@example.com',
                'password': 'password123',
                'department_name': 'Test Department',
                'role': 'employee'
                }
            response = client.post('/add_user', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('view_users'))



    @patch('app.get_db_connection')
    def test_delete_user_success(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value

        with app.test_client() as client:
            data = {'email': 'test@example.com'}  
            response = client.post('/delete_user', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('delete_user'))  



    @patch('app.get_db_connection')  
    def test_view_users(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []  

        with app.test_client() as client:
            response = client.get('/view_users')

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Users', response.data)



    @patch('app.get_db_connection')
    def test_add_department_success(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value

        with app.test_client() as client:
            data = {'department_name': 'Test Department'}
            response = client.post('/add_department', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('add_department'))  



    @patch('app.get_db_connection')
    def test_delete_department_success(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value

        with app.test_client() as client:
            data = {'name': 'Test Department'} 
            response = client.post('/delete_department', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('delete_department'))  



    @patch('app.get_db_connection')  
    def test_view_departments(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []  

        with app.test_client() as client:
            response = client.get('/view_departments')

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Departments', response.data)  



    @patch('app.get_db_connection')
    def test_view_requests_success(self, mock_get_db_connection):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'manager@example.com'

            mock_cursor = mock_get_db_connection.return_value.cursor.return_value
            mock_cursor.dictionary = True  
            mock_cursor.fetchone.return_value = {'department_name': 'Engineering'}
            mock_cursor.fetchall.return_value = [
                {
                    'id': 1,
                    'email': 'user@example.com',
                    'expense_type': 'Travel',
                    'amount': 100.00,
                    'date': '2024-06-22',
                    'status': 'pending',
                    'comment': '',
                }
            ]

            response = client.get('/view_requests')
            self.assertEqual(response.status_code, 200)
            html_content = response.get_data(as_text=True)  
            self.assertRegex(html_content, r'<h1>Pending Reimbursement Requests</h1>')  



    @patch('app.get_db_connection')
    def test_view_processed_requests_success(self, mock_get_db_connection):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'manager@example.com'

            mock_cursor = mock_get_db_connection.return_value.cursor.return_value
            mock_cursor.dictionary = True  
            mock_cursor.fetchone.return_value = {'department_name': 'Engineering'}
            mock_cursor.fetchall.return_value = [
                {
                    'id': 1,
                    'email': 'user@example.com',
                    'expense_type': 'Travel',
                    'amount': 100.00,
                    'date': '2024-06-22',
                    'status': 'approved',  
                    'comment': '',
                }
            ]

            response = client.get('/view_processed_requests')
            self.assertEqual(response.status_code, 200)
            html_content = response.get_data(as_text=True)  # Decode as text
            self.assertRegex(html_content, r'<h1>Processed Reimbursement Requests</h1>')  # Assuming a table header



    @patch('app.get_db_connection')
    def test_update_request_success(self, mock_get_db_connection):
        mock_conn = mock_get_db_connection.return_value

        with app.test_client() as client:
            data = {
                'id': 1,  
                'status': 'Approved',
                'comment': 'Request approved for reimbursement.'
            }
            response = client.post('/update_request', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, url_for('view_requests'))  



    @patch('app.get_db_connection')  
    def test_claim_reimbursement_form_success(self, mock_get_db_connection):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'user@example.com'  

            response = client.get('/claim_reimbursement_form')

        
            self.assertEqual(response.status_code, 200)
            html_content = response.get_data(as_text=True)  
            self.assertRegex(html_content, r'<h1>Claim Reimbursement</h1>')  



    @patch('app.get_db_connection')
    def test_claim_reimbursement_success(self, mock_get_db_connection):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'user@example.com'

            data = {
            'expense_type': 'Travel',
            'amount': '100.00',
            'date': '2024-06-22',
            }
            response = client.post('/claim_reimbursement', data=data)

            self.assertEqual(response.status_code, 200)
            html_content = response.get_data(as_text=True)
            self.assertRegex(html_content, r'<h1>Reimbursement Request Submitted</h1>') 



    @patch('app.get_db_connection')
    def test_view_requests_employee_success(self, mock_get_db_connection):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['email'] = 'user@example.com'

            mock_cursor = mock_get_db_connection.return_value.cursor.return_value
            mock_cursor.dictionary = True  
            mock_cursor.fetchall.return_value = [
                {
                    'id': 1,
                    'email': 'user@example.com',
                    'expense_type': 'Travel',
                    'amount': 100.00,
                    'date': '2024-06-22',
                    'status': 'pending',
                    'comment': '',
                }
            ]

            response = client.get('/view_requests_employee')
        
            self.assertEqual(response.status_code, 200)
            html_content = response.get_data(as_text=True) 
            self.assertRegex(html_content, r'<th>Expense Type</th>')  


if __name__ == '__main__':
    unittest.main()
