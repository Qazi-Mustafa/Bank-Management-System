import sys
from PyQt6 import QtWidgets, uic 
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QTimer
from datetime import datetime,date, timedelta
import pyodbc
from decimal import Decimal



# Function to connect to the database
def connect_to_database():
    server = 'MUSTAFA'  # Replace with your server name
    database = 'Bank_Managment_System'  # Replace with your database name
    use_windows_authentication = True  # or False, if you're not using Windows Authentication

    try:
        if use_windows_authentication:
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            connection = pyodbc.connect(connection_string, timeout=10)
            print("Connection to SQL Server successful.")
            return connection
    except Exception as e:
        print(f"An error occurred while connecting to SQL Server: {e}")
        return None
    
def relaunch_initial_ui(connection):
    global FirstWindow
    # First, we check if the first window is already open, if not, we create it again.
    if FirstWindow is None or not QtWidgets.QWidget.isVisible(FirstWindow):
        FirstWindow = QtWidgets.QMainWindow()
        first_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\firstwindow.ui", FirstWindow)
        first_ui.login_button_admin.clicked.connect(lambda: [FirstWindow.close(), launch_employee_login_ui(connection)])
        first_ui.login_button_customer.clicked.connect(lambda: [FirstWindow.close(), launch_customer_login_ui(connection)])

    # We then show the first window again.
    FirstWindow.show()
global AccountDetailsWindow
AccountDetailsWindow = None
def launch_account_details_ui(customer_email, connection):
    global AccountDetailsWindow

    if AccountDetailsWindow is None or not QtWidgets.QWidget.isVisible(AccountDetailsWindow):
        AccountDetailsWindow = QtWidgets.QMainWindow()
        uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\Account_details.ui", AccountDetailsWindow)

        # Fetch user_id and display customer and account details
        user_id = display_customer_account_details(customer_email, connection)
        if user_id:
            AccountDetailsWindow.gotosavings.clicked.connect(lambda: handle_gotosavings_click(customer_email, connection))
            AccountDetailsWindow.applyforlaon.clicked.connect(lambda: launch_loan_application_ui(connection, user_id))
            AccountDetailsWindow.funds.clicked.connect(lambda: launch_current_account_ui(connection, user_id))
            AccountDetailsWindow.review_button.clicked.connect(lambda: launch_customer_review_ui(connection,user_id))
            
        # Show the window
        AccountDetailsWindow.show()
    else:
        print("Account Details Window is already open.")


global CustomerReviewWindow
CustomerReviewWindow = None

# This function will be called when the review button is clicked
def launch_customer_review_ui(user_id, connection):
    global CustomerReviewWindow
    try:
        if CustomerReviewWindow is None or not QtWidgets.QWidget.isVisible(CustomerReviewWindow):
            CustomerReviewWindow = QtWidgets.QDialog()
            ui_path = r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\customer_review.ui"
            uic.loadUi(ui_path, CustomerReviewWindow)

            # Connect the 'post' button click to the on_post_button_clicked function
            post_button = CustomerReviewWindow.findChild(QtWidgets.QPushButton, "post")
            post_button.clicked.connect(lambda: on_post_button_clicked(user_id, connection))


            CustomerReviewWindow.show()
        else:
            CustomerReviewWindow.activateWindow()
    except Exception as e:
        print(f"An error occurred while launching the customer review UI: {e}")


def on_post_button_clicked(connection, user_id):
    try:

        # Attempt to find the QTextEdit widget by its object name
        review_text_edit = CustomerReviewWindow.findChild(QtWidgets.QTextEdit, "review")
        
        # Check if the QTextEdit widget was successfully retrieved
        if review_text_edit is None:
            raise Exception("The QTextEdit named 'review' was not found. Check the object name in the UI file.")
        
        # Retrieve the text content from the QTextEdit widget
        review_text = review_text_edit.toPlainText()
        # Check if the review text is empty
        if not review_text.strip():
            QMessageBox.warning(CustomerReviewWindow, "Empty Review", "The review text cannot be empty.")
            return
        # Retrieve the credit score of the user for inclusion in the review
        print(f"Type of user_id: {type(user_id)}")
        print(f"Type of connection: {type(connection)}")
        cursor = connection.cursor()
        cursor.execute("SELECT credit_score FROM Customer WHERE user_id = ?", (user_id,))
        credit_score_result = cursor.fetchone()
        print("check 3")
        if credit_score_result:
            credit_score = credit_score_result[0]
            # SQL query to insert review into the customer_review table
            insert_query = """
                INSERT INTO customer_review (user_id, credit_score, customer_review) 
                VALUES (?, ?, ?)
            """
            cursor.execute(insert_query, (user_id, credit_score, review_text))
            connection.commit()

            # Display a success message
            QMessageBox.information(CustomerReviewWindow, "Review Posted", "Your review has been successfully posted.")
        else:
            QMessageBox.warning(CustomerReviewWindow, "Error", "Could not retrieve credit score for the user.")

    except Exception as e:
        QMessageBox.warning(CustomerReviewWindow, "Error", f"An error occurred while posting the review: {e}")
        print(f"An error occurred while posting the review: {e}")
    finally:
        # Ensure the cursor is closed after operation
        cursor.close()

    

def show_login_failure_popup(parent_ui, text):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Login Failed")
    msg_box.setText(text)

    # Create a QTimer to close the popup after 2 seconds
    timer = QTimer()
    timer.timeout.connect(msg_box.close)
    timer.start(2000)  # 2000 milliseconds = 2 seconds

    msg_box.exec()

def handle_employee_login_click(ui, connection):
    employee_id = ui.ID_line.text()
    employee_email = ui.Email_line.text()
    employee_password = ui.pass_employee_line.text()

    try:
        with connection.cursor() as cursor:
            # Retrieve the department of the employee
            cursor.execute("""
                SELECT d.department_name
                FROM Employee e
                JOIN Department d ON e.department_id = d.department_id
                WHERE e.employee_id = ? AND e.employee_email = ?
                """, (employee_id, employee_email))

            result = cursor.fetchone()

            # If the employee exists, proceed to check the password
            if result:
                department_name = result[0]
                # Based on the department, set the appropriate table to check the password
                department_tables = {
                    'Investment_Management': 'Investment_Manager',
                    'Human_Resources': 'Admin',
                    'Accounts': 'Accountant',
                    'Customer_Services': 'Customer_Service_Representative'
                }
                password_table = department_tables.get(department_name)

                # If the department is recognized, check the password
                if password_table:
                    cursor.execute(f"SELECT employee_password FROM {password_table} WHERE employee_id = ?", (employee_id,))
                    password_result = cursor.fetchone()
                    if password_result and password_result[0] == employee_password:
                        ui.close()  # Close the login window

                        # Launch different UIs based on department
                        if department_name == 'Investment_Management':
                            launch_investment_manager_ui(connection)
                        elif department_name == 'Human_Resources':
                            launch_human_resources_ui(connection)
                        elif department_name == 'Accounts':
                            launch_accountant_ui(connection)
                        elif department_name == 'Customer_Services':
                            launch_customer_service_ui(connection)

                        print("True")  # Password matches
                    else:
                        show_login_failure_popup(ui, "Password does not match")
                        print("False")  # Password does not match
                else:
                    show_login_failure_popup(ui, "Department not recognized")
                    print("False")  # Department not recognized
            else:
                show_login_failure_popup(ui, "Employee ID and email do not match")
                print("False")  # Employee ID and email do not match

    except Exception as e:
        print(f"An error occurred: {e}")
        print("False")  # An error occurred, print False

# Add functions for launching UIs for other departments
def launch_investment_manager_ui(connection):
    # Implement the UI for the Investment Manager here
    launch_reviewloans_ui(connection)

def launch_human_resources_ui(connection):
    # Implement the UI for the Human Resources department here
    launch_employee_management_ui(connection)

def launch_accountant_ui(connection):
    # Implement the UI for the Accountant department here
    launch_balance_sheet_ui(connection)

def launch_customer_service_ui(connection):
    # Implement the UI for the Customer Service department here
        launch_mainreview_ui(connection)



# Function to handle the login button click for customer
def handle_customer_login_click(ui, connection):
    customer_email = ui.username_line.text()  # Get the email from the input
    customer_password = ui.password_line.text()  # Get the password from the input
    cursor = connection.cursor()

    # SQL query to check if the customer's email exists
    try:
        cursor.execute("SELECT COUNT(*) FROM Customer WHERE user_email = ?", (customer_email,))
        (email_match_count,) = cursor.fetchone()

        if email_match_count > 0:
            # Additional query to check if the customer's password matches the email
            cursor.execute("SELECT COUNT(*) FROM Customer WHERE user_email = ? AND password = ?", (customer_email, customer_password))
            (password_match_count,) = cursor.fetchone()

            if password_match_count > 0:
                    
                    launch_account_details_ui(customer_email, connection) # Email and password combination is correct
                    print("True")
            else:
                show_login_failure_popup(ui,"Customer login failed: Incorrect password")
                print("Customer login failed: Incorrect password")  # Password is incorrect
        else:
            show_login_failure_popup(ui,"Customer login failed: Email does not exist")
            print("Customer login failed: Email does not exist")  # Email does not exist
    except Exception as e:
        print(f"An error occurred during customer login: {e}")
    finally:
        cursor.close()

def display_customer_account_details(customer_email, connection):
    try:
        cursor = connection.cursor()
        # Fetch customer details
        cursor.execute("SELECT user_id, user_first_name, user_last_name, user_dob, user_number, credit_score FROM Customer WHERE user_email = ?", (customer_email,))
        user_details = cursor.fetchone()

        if user_details:
            user_id, first_name, last_name, dob, number, credit_score = user_details

            # Use user_id to fetch account details
            cursor.execute("SELECT account_no, account_balance FROM Account WHERE user_id = ?", (user_id,))
            account_result = cursor.fetchone()
            if account_result:
                account_no, balance = account_result

                # Update the UI for account details
                AccountDetailsWindow.title.setText(str(account_no))
                AccountDetailsWindow.balance.setText(str(balance))

            # Update the UI for customer details
            AccountDetailsWindow.first_name_customer.setText(first_name)
            AccountDetailsWindow.last_name_customer.setText(last_name)
            AccountDetailsWindow.date_of_birth_customer.setText(str(dob))
            AccountDetailsWindow.number_customer.setText(str(number))
            AccountDetailsWindow.creditscore.setText(str(credit_score))

            # Set line edits to read-only
            AccountDetailsWindow.first_name_customer.setReadOnly(True)
            AccountDetailsWindow.last_name_customer.setReadOnly(True)
            AccountDetailsWindow.date_of_birth_customer.setReadOnly(True)
            AccountDetailsWindow.number_customer.setReadOnly(True)
            AccountDetailsWindow.creditscore.setReadOnly(True)
            AccountDetailsWindow.title.setReadOnly(True)
            AccountDetailsWindow.balance.setReadOnly(True)

            return user_id  # Return user_id

        else:
            print("No customer details found for the given email.")
            return None

    except Exception as e:
        print(f"An error occurred while fetching customer details: {e}")
        return None
    

def fetch_loan_approval_data(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM loan_approval"  # Adjust the query as needed to match your table structure
        cursor.execute(query)
        return cursor.fetchall()  # Fetches all records from the loan_approval table
    except Exception as e:
        print(f"Error fetching loan approval data: {e}")
        return []

def populate_loan_table(loan_table, data):
    loan_table.setRowCount(len(data))
    loan_table.setColumnCount(4)  # Set the number of columns (adjust based on your table)

    for row_index, row_data in enumerate(data):
        for col_index, item in enumerate(row_data):
            loan_table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(item)))


global ReviewLoansWindow
ReviewLoansWindow = None

def launch_reviewloans_ui(connection):
    global ReviewLoansWindow

    if ReviewLoansWindow is None or not QtWidgets.QWidget.isVisible(ReviewLoansWindow):
        ReviewLoansWindow = QtWidgets.QMainWindow()
        review_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\reviewLoans.ui", ReviewLoansWindow)

        loan_table = review_ui.findChild(QtWidgets.QTableWidget, "loan_table")
        loan_approval_data = fetch_loan_approval_data(connection)
        populate_loan_table(loan_table, loan_approval_data)

        # Connect cell clicked signal to a function
        loan_table.cellClicked.connect(lambda row, col: on_loan_table_cell_clicked(row, col, connection))

        ReviewLoansWindow.show()
    else:
        ReviewLoansWindow.activateWindow()

def on_loan_table_cell_clicked(row, col, connection):
    # Here you can add code to fetch specific loan data based on the clicked row
    # For now, just print the cell value or open the mainloan UI
    loan_id = ReviewLoansWindow.findChild(QtWidgets.QTableWidget, "loan_table").item(row, 0).text()  # Assuming first column is loan_id
    print("Clicked on loan ID:", loan_id)
    launch_mainloan_ui(connection, loan_id)

global MainReviewWindow
MainReviewWindow = None
def launch_mainreview_ui(connection):
    global MainReviewWindow

    if MainReviewWindow is None or not QtWidgets.QWidget.isVisible(MainReviewWindow):
        MainReviewWindow = QtWidgets.QMainWindow()
        main_review_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\mainreview.ui", MainReviewWindow)

        reviews_table = main_review_ui.findChild(QtWidgets.QTableWidget, "reviews_table")
        customer_review_data = fetch_customer_review_data(connection)  # Use the new function here
        populate_loan_table(reviews_table, customer_review_data)

        MainReviewWindow.show()
    else:
        MainReviewWindow.activateWindow()

def fetch_customer_review_data(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM customer_review"  # Adjust the query as needed to match your table structure
        cursor.execute(query)
        return cursor.fetchall()  # Fetches all records from the customer_review table
    except Exception as e:
        print(f"Error fetching customer review data: {e}")
        return []



global MainLoanWindow
MainLoanWindow = None
def launch_mainloan_ui(connection, loan_id):
    global MainLoanWindow

    print("Launching main loan UI...")  # Debug print
    if MainLoanWindow is None or not QtWidgets.QWidget.isVisible(MainLoanWindow):
        MainLoanWindow = QtWidgets.QMainWindow()
        mainloan_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\mainloan.ui", MainLoanWindow)

        # Connect Approve button
        approve_button = mainloan_ui.findChild(QtWidgets.QPushButton, "Approve")
        if approve_button:
            approve_button.clicked.connect(lambda: on_approve_clicked(connection, mainloan_ui))

        # Connect Decline button
        decline_button = mainloan_ui.findChild(QtWidgets.QPushButton, "Decline")
        if decline_button:
            decline_button.clicked.connect(lambda: on_decline_clicked(connection, mainloan_ui))


        print(f"Fetching details for loan ID: {loan_id}")  # Debug print
        try:
            loan_details = fetch_full_loan_details(connection, loan_id)
            if loan_details:
                print("Populating main loan UI...")  # Debug print
                populate_mainloan_ui(mainloan_ui, loan_details, connection)
            else:
                print("No loan details found.")  # Debug print
        except Exception as e:
            print(f"Error fetching loan details: {e}")  # Error print

        MainLoanWindow.show()
        print("Main loan UI should now be visible.")  # Debug print
    else:
        MainLoanWindow.activateWindow()
        print("Main loan UI already open, bringing to front.")  # Debug print



def fetch_full_loan_details(connection, loan_id):
    try:
        cursor = connection.cursor()

        # Fetch the loan approval details
        cursor.execute("""
            SELECT la.loan_type, la.amount, c.user_id, c.user_first_name + ' ' + c.user_last_name AS customer_name, 
                   a.account_balance, c.credit_score
            FROM loan_approval la
            JOIN Customer c ON la.user_id = c.user_id
            JOIN Account a ON c.user_id = a.user_id
            WHERE la.request_id = ?
        """, (loan_id,))
        loan_approval_details = cursor.fetchone()

        # Fetch the customer's previous loans
        cursor.execute("""
            SELECT Loan_ID, Amount_Loaned, Loan_Status 
            FROM Loan 
            WHERE User_ID = ?
        """, (loan_approval_details[2],)) # Assuming the third value is the user_id
        previous_loans = cursor.fetchall()

        return loan_approval_details, previous_loans
    except Exception as e:
        print(f"Error fetching loan approval details: {e}")
        return None, None
    
def populate_mainloan_ui(mainloan_ui, loan_details, connection):
    try:
        # Unpack all the details fetched from the database
        loan_type, amount, user_id, customer_name, account_balance, credit_score, previous_loans = loan_details

        # Set the values in the UI components
        mainloan_ui.findChild(QtWidgets.QLineEdit, "custID").setText(str(user_id))
        mainloan_ui.findChild(QtWidgets.QLineEdit, "custName").setText(customer_name)
        mainloan_ui.findChild(QtWidgets.QLineEdit, "Loan_type").setText(loan_type)
        mainloan_ui.findChild(QtWidgets.QLineEdit, "Loan_Amount").setText(str(amount))
        mainloan_ui.findChild(QtWidgets.QLineEdit, "AccountB").setText(str(account_balance))
        
        # Check the credit score box if credit score is above 670
        credit_checkbox = mainloan_ui.findChild(QtWidgets.QCheckBox, "Creditscore")
        credit_checkbox.setChecked(credit_score > 670)
        credit_checkbox.setEnabled(False)  # Assuming you don't want the user to change this checkbox
        
        # Populate the loan table with the previous loans
        loan_table = mainloan_ui.findChild(QtWidgets.QTableWidget, "loan_table")
        loan_table.setRowCount(len(previous_loans))
        for row_index, loan in enumerate(previous_loans):
            loan_table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(loan[0]))) # loan_id
            loan_table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(loan[1]))) # loan_amount
            loan_table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(loan[2]))      # loan_status

    except Exception as e:
        print(f"An error occurred while populating the main loan UI: {e}")

def fetch_full_loan_details(connection, loan_id):
    try:
        cursor = connection.cursor()

        # Fetch the loan approval details along with customer and account information
        cursor.execute("""
            SELECT la.loan_type, la.amount, c.user_id, c.user_first_name + ' ' + c.user_last_name AS customer_name, 
                   a.account_balance, c.credit_score
            FROM loan_approval la
            JOIN Customer c ON la.user_id = c.user_id
            JOIN Account a ON c.user_id = a.user_id
            WHERE la.request_id = ?
        """, (loan_id,))
        loan_approval_details = cursor.fetchone()

        if not loan_approval_details:
            raise ValueError(f"No loan approval details found for loan_id={loan_id}")

        # Unpack the fetched loan approval details
        loan_type, amount, user_id, customer_name, account_balance, credit_score = loan_approval_details

        # Fetch the customer's previous loans
        cursor.execute("""
            SELECT Loan_ID, Amount_Loaned, Loan_Status 
            FROM Loan 
            WHERE User_ID = ?
        """, (user_id,))
        previous_loans = cursor.fetchall()

        return loan_type, amount, user_id, customer_name, account_balance, credit_score, previous_loans
    except Exception as e:
        print(f"Error fetching full loan details: {e}")
        return None

def fetch_account_balance(connection, user_id):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT account_balance FROM accounts WHERE user_id = ?", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching account balance: {e}")
        return None

def fetch_customer_details(connection, user_id):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_first_name, credit_score FROM Customer WHERE user_id = ?", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching customer details: {e}")
        return None

def handle_gotosavings_click(customer_email, connection):
    try:
        cursor = connection.cursor()

        # Fetch user_id from Customer table using the email
        cursor.execute("SELECT user_id FROM Customer WHERE user_email = ?", (customer_email,))
        user_id_result = cursor.fetchone()
        if user_id_result is None:
            QMessageBox.information(None, "Error", "User not found.")
            return
        user_id = user_id_result[0]

        # Now check for the saving_account_id in the Account table using the user_id
        cursor.execute("SELECT saving_account_id FROM Account WHERE user_id = ?", (user_id,))
        saving_account_result = cursor.fetchone()
        
        if saving_account_result and saving_account_result[0] is not None:
            saving_account_id = saving_account_result[0]
            launch_savings_account_details_ui(saving_account_id, connection)
        else:
            QMessageBox.information(None, "No Savings Account", "No savings account found for this user.")

    except Exception as e:
        print(f"An error occurred while checking for a savings account: {e}")
        QMessageBox.warning(None, "Error", "An error occurred while checking for a savings account.")


def get_new_loan_id(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(Loan_ID) FROM Loan")
        max_id = cursor.fetchone()[0]
        return max_id + 1 if max_id is not None else 1
    except Exception as e:
        print(f"Error getting new loan ID: {e}")
        return None

def approve_loan(connection, user_id, loan_type, loan_amount, interest_rate, mainloan_ui):
    try:
        cursor = connection.cursor()

        # Get a new loan ID
        new_loan_id = get_new_loan_id(connection)

        if new_loan_id is None:
            print("Could not retrieve a new loan ID.")
            return

        loan_amount_proper_type = float(loan_amount)
        
        # Corrected line: Using datetime.date.today() to get the current date
        payback_plan_date = date.today() + timedelta(days=365)
        estimated_payback_plan = payback_plan_date.strftime('%Y-%m-%d')
        # Fetch the highest loan number for the user and add 1 to it for the new loan_number
        cursor.execute("SELECT COALESCE(MAX(Loan_number), 0) + 1 FROM Loan WHERE User_ID = ?", (user_id,))
        loan_number = cursor.fetchone()[0]

        # Insert new loan with 'due' status and new loan id
        insert_query = """INSERT INTO Loan (Loan_ID, User_ID, Loan_Status, Interest_Rate, Loan_Type, 
                         Amount_Loaned, Estimated_Payback_Plan, Loan_number) 
                         VALUES (?, ?, 'due', ?, ?, ?, ?, ?)"""
        cursor.execute(insert_query, (new_loan_id, user_id, interest_rate, loan_type, loan_amount_proper_type, 
                                      estimated_payback_plan, loan_number))
        connection.commit()
        # Delete the loan_approval request
        delete_query = "DELETE FROM loan_approval WHERE user_id = ? AND amount = ? AND loan_type = ?"
        cursor.execute(delete_query, (user_id, loan_amount_proper_type, loan_type))
        
        if cursor.rowcount > 0:
            print(f"Deleted {cursor.rowcount} records from loan_approval table.")
            connection.commit()
        else:
            print(f"No records found to delete in loan_approval table with user_id={user_id}, amount={loan_amount_proper_type}, loan_type={loan_type}")

        mainloan_ui.close()  # Close the MainLoanWindow after the operation is complete.
        print("Loan approved and corresponding loan_approval request deleted.")

    except Exception as e:
        print(f"Error in approving loan: {e}")
        connection.rollback()
    finally:
        cursor.close()

def decline_loan(connection, user_id, loan_type, loan_amount, mainloan_ui):
    try:
        cursor = connection.cursor()

        # Convert the loan amount to the correct data type if necessary, assuming it's passed as a string
        loan_amount = Decimal(loan_amount) if isinstance(loan_amount, str) else loan_amount

        # Delete the loan_approval request
        delete_query = """
        DELETE FROM loan_approval 
        WHERE user_id = ? AND amount = ? AND loan_type = ?
        """
        cursor.execute(delete_query, (user_id, loan_amount, loan_type))
        rows_deleted = cursor.rowcount
        connection.commit()

        if rows_deleted > 0:
            print(f"Loan request declined. Removed {rows_deleted} record(s) from loan_approval table.")
            QMessageBox.information(mainloan_ui, "Loan Declined", "The loan request has been declined and removed from the system.")
        else:
            print("No matching loan_approval request found to delete.")
            QMessageBox.information(mainloan_ui, "No Action Taken", "No matching loan request found to decline.")

    except Exception as e:
        print(f"Error in declining loan request: {e}")
        connection.rollback()
        QMessageBox.critical(mainloan_ui, "Error", f"An error occurred while declining the loan request: {e}")
    finally:
        cursor.close()
        mainloan_ui.close()  # Close the MainLoanWindow after the operation is complete.



def on_decline_clicked(connection, mainloan_ui):
    try:
        user_id_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "custID")
        loan_type_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "Loan_type")
        loan_amount_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "Loan_Amount")

        if not all([user_id_widget, loan_type_widget, loan_amount_widget]):
            print("One or more widgets not found")
            return

        user_id = user_id_widget.text()
        loan_type = loan_type_widget.text()
        loan_amount = loan_amount_widget.text()

        print(f"User ID: {user_id}, Loan Type: {loan_type}, Loan Amount: {loan_amount}")  # Debug print

        # Call the function to decline the loan and pass the mainloan_ui to it
        decline_loan(connection, user_id, loan_type, loan_amount, mainloan_ui)
        print("Loan request declined successfully")  # Debug print
    except Exception as e:
        print(f"Error in on_decline_clicked: {e}")  # Error print


def on_approve_clicked(connection, mainloan_ui):
    print("Approve button clicked")  # Debug print
    try:
        user_id_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "custID")
        loan_type_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "Loan_type")
        loan_amount_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "Loan_Amount")
        interest_rate_widget = mainloan_ui.findChild(QtWidgets.QLineEdit, "IR")

        if not all([user_id_widget, loan_type_widget, loan_amount_widget, interest_rate_widget]):
            print("One or more widgets not found")
            return

        user_id = user_id_widget.text()
        loan_type = loan_type_widget.text()
        loan_amount = loan_amount_widget.text()
        interest_rate = interest_rate_widget.text()

        print(f"User ID: {user_id}, Loan Type: {loan_type}, Loan Amount: {loan_amount}, Interest Rate: {interest_rate}")  # Debug print

        # Call the function to approve the loan and pass the mainloan_ui to it
        approve_loan(connection, user_id, loan_type, loan_amount, interest_rate, mainloan_ui)
        print("Loan approved successfully")  # Debug print
    except Exception as e:
        print(f"Error in on_approve_clicked: {e}")  # Error print



def check_savings_account(user_id, connection):
    try:
        cursor = connection.cursor()

        # Check for saving_account_id in Account table
        cursor.execute("SELECT saving_account_id FROM Account WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            saving_account_id = result[0]
            launch_savings_account_details_ui(saving_account_id, connection)
        else:
            QMessageBox.information(None, "No Savings Account", "No savings account found for this user.")

    except Exception as e:
        print(f"An error occurred while checking for a savings account: {e}")
        QMessageBox.warning(None, "Error", "An error occurred while checking for a savings account.")

def fetch_savings_account_details_and_calculate_payment(saving_account_id, connection):
    try:
        cursor = connection.cursor()

        # Fetch details from the savings account table
        cursor.execute("""
            SELECT saving_account_balance, interest_type, interest_rate, payout_duration, saving_account_period 
            FROM interest_type
            WHERE saving_account_id = ?
        """, (saving_account_id,))
        account_details = cursor.fetchone()

        if not account_details:
            return None, "Savings account not found."

        # Extract the details
        balance, interest_type, interest_rate, payout_duration, periods_left = account_details

        # Calculate the payment based on the interest type
        if interest_type == 'Simple Interest':
            # P = Principal amount (initial investment)
            # r = annual interest rate (decimal)
            # t = time the money is invested for (in years)
            # n = number of times that interest is compounded per year
            # A = amount of money accumulated after n years, including interest.

            # Convert annual interest rate to the rate per payout period
            if payout_duration == 'Yearly':
                t = 1
            elif payout_duration == 'Quarterly':
                interest_rate /= 4
                t = 0.25
            elif payout_duration == 'Monthly':
                interest_rate /= 12
                t = 1/12

            # Convert interest rate to decimal
            r = interest_rate / 100

            # Calculate payment for simple interest
            payment = balance * r * t

        elif interest_type == 'Compound Interest':
            # A = P(1 + r/n)^(nt)
            if payout_duration == 'Yearly':
                n = 1
                t = 1
            elif payout_duration == 'Quarterly':
                n = 4
                t = 0.25
            elif payout_duration == 'Monthly':
                n = 12
                t = 1/12

            # Assuming balance and interest_rate are initially decimal.Decimal
            balance = float(balance)
            interest_rate = float(interest_rate) / 100  # convert percentage to decimal

            # Then perform your calculation
            payment = balance * (1 + interest_rate/n)**(n*t) - balance

        # Format the payment to two decimal places
        payment = round(payment, 2)

        # Return the calculated details
        return {
            'account_no': saving_account_id,
            'balance': balance,
            'interest_type': interest_type,
            'payment': payment,
            'duration': payout_duration,
            'periods_left': periods_left
        }, None

    except Exception as e:
        return None, str(e)





# Function to launch the customer login UI
def launch_customer_login_ui(connection):
    CustomerLoginWindow = QtWidgets.QDialog()
    customer_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\login.ui", CustomerLoginWindow)
    customer_ui.login_button.clicked.connect(lambda: handle_customer_login_click(customer_ui, connection))
    CustomerLoginWindow.exec()  # Use exec() to make it modal

def launch_employee_login_ui(connection, first_window=None):
    global FirstWindow
    FirstWindow = first_window  # Assign the passed first window to the global FirstWindow
    EmployeeLoginWindow = QtWidgets.QMainWindow()
    employee_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\EmployeeLogin.ui", EmployeeLoginWindow)
    
    # Handle login attempt
    employee_ui.login_button_employee.clicked.connect(lambda: handle_employee_login_click(employee_ui, connection))
    
    # Handle back button click to return to the first window
    employee_ui.back_button_employee.clicked.connect(lambda: relaunch_initial_ui(connection))
    
    EmployeeLoginWindow.show() 

global SavingsAccountDetailsWindow
SavingsAccountDetailsWindow = None
def launch_savings_account_details_ui(saving_account_id, connection):
    global SavingsAccountDetailsWindow

    # Create the window if it doesn't exist or is not visible
    if SavingsAccountDetailsWindow is None or not QtWidgets.QWidget.isVisible(SavingsAccountDetailsWindow):
        SavingsAccountDetailsWindow = QtWidgets.QMainWindow()
        savings_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\savings_account_details.ui", SavingsAccountDetailsWindow)

        # Fetch and calculate the savings account details
        details, error = fetch_savings_account_details_and_calculate_payment(saving_account_id, connection)
        if error:
            QMessageBox.warning(savings_ui, "Error", f"An error occurred while fetching the savings account details: {error}")
            return
        else:
            # Update the UI with the fetched details
            savings_ui.findChild(QtWidgets.QLineEdit, "saving_accountno").setText(details['account_no'])
            savings_ui.findChild(QtWidgets.QLineEdit, "saving_balance").setText(str(details['balance']))
            savings_ui.findChild(QtWidgets.QLineEdit, "interest_type").setText(details['interest_type'])
            savings_ui.findChild(QtWidgets.QLineEdit, "payment").setText(str(details['payment']))
            savings_ui.findChild(QtWidgets.QLineEdit, "duration").setText(details['duration'])
            savings_ui.findChild(QtWidgets.QLineEdit, "periods_left").setText(str(details['periods_left']))

    # Show the window
    SavingsAccountDetailsWindow.show()


def on_loan_table_cell_clicked(row, col, connection):
    # Assuming the first column of your loan_table has the loan_id
    loan_id = ReviewLoansWindow.findChild(QtWidgets.QTableWidget, "loan_table").item(row, 0).text()
    launch_mainloan_ui(connection, loan_id)


def fetch_user_loan_details(user_id, connection):
    try:
        cursor = connection.cursor()
        query = "SELECT Loan_ID, Amount_Loaned, Loan_Status FROM Loan WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()  # Fetches all loan records for the user
    except Exception as e:
        print(f"Error fetching loan details: {e}")
        return []
    


def update_loan_table(user_id, connection, loan_window):
    loan_details = fetch_user_loan_details(user_id, connection)
    loan_table = loan_window.findChild(QtWidgets.QTableWidget, "loan_table")
    loan_table.setRowCount(len(loan_details))

    for row_index, loan in enumerate(loan_details):
        for col_index, item in enumerate(loan):
            loan_table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(item)))

global LoanApplicationWindow
LoanApplicationWindow = None

def launch_loan_application_ui(connection, user_id):
    global LoanApplicationWindow

    if LoanApplicationWindow is None or not QtWidgets.QWidget.isVisible(LoanApplicationWindow):
        LoanApplicationWindow = QtWidgets.QMainWindow()
        uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\applyloan.ui", LoanApplicationWindow)
        
        populate_loan_type_combo(LoanApplicationWindow)
        update_loan_table(user_id, connection, LoanApplicationWindow)
        
        # Connect the apply loan button click to the handler function
        apply_loan_button = LoanApplicationWindow.findChild(QtWidgets.QPushButton, "Apply_loan_button")
        apply_loan_button.clicked.connect(lambda: handle_apply_loan_click(user_id, connection, LoanApplicationWindow))

    LoanApplicationWindow.show()

def handle_apply_loan_click(user_id, connection, loan_window):
    try:
        # Retrieve the loan amount from the UI
        loan_amount_text = loan_window.findChild(QtWidgets.QLineEdit, "loan_amount_line").text()

        # Check if the loan amount field is empty
        if not loan_amount_text:
            QMessageBox.warning(loan_window, "Error", "Please enter a loan amount.")
            return

        # Convert loan amount to integer
        loan_amount = int(loan_amount_text)

        # Retrieve the loan type from the UI
        loan_type = loan_window.findChild(QtWidgets.QComboBox, "loan_type_combo").currentText()

        # Prepare SQL query to insert loan request
        insert_query = "INSERT INTO loan_approval (user_id, amount, loan_type) VALUES (?, ?, ?)"

        
        # Execute the insert query
        cursor = connection.cursor()
        cursor.execute(insert_query, (user_id, loan_amount, loan_type))
        connection.commit()

        print("Loan request successfully submitted.")
        QMessageBox.information(loan_window, "Success", "Your loan request has been submitted.")
        
    except ValueError:
        # This block catches errors converting loan amount to an integer
        print("Invalid loan amount entered.")
        QMessageBox.warning(loan_window, "Error", "Please enter a valid loan amount.")
    except Exception as e:
        print(f"Error submitting loan request: {e}")
        QMessageBox.warning(loan_window, "Error", "An error occurred while submitting your loan request.")


def populate_loan_type_combo(window):
    # Assuming 'loan_type_combo' is the name of the combobox widget in your applyloan.ui
    loan_type_combo = window.findChild(QtWidgets.QComboBox, "loan_type_combo")
    
    # List of loan options
    loan_options = [
        "Mortgage",
        "Student Loan",
        "Home Equity Loan",
        "Car Loan",
        "Personal Loan",
        "Business Loan",
        "Debt Consolidation"
    ]

    # Clear any existing items in the combobox
    loan_type_combo.clear()

    # Add the loan options to the combobox
    loan_type_combo.addItems(loan_options)


global current_account_details
current_account_details = None
def launch_current_account_ui(connection, user_id):
    global current_account_details

    if current_account_details is None or not QtWidgets.QWidget.isVisible(current_account_details):
        current_account_details = QtWidgets.QMainWindow()
        uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\current_account_details.ui", current_account_details)

        # Connect deposit and transfer buttons to their respective functions
        deposit_button = current_account_details.findChild(QtWidgets.QPushButton, "deposit")
        deposit_button.clicked.connect(lambda: on_deposit_button_clicked(connection, user_id))

        transfer_button = current_account_details.findChild(QtWidgets.QPushButton, "transfer")
        transfer_button.clicked.connect(lambda: on_transfer_button_clicked(connection, user_id))

    current_account_details.show()

global DepositWindow
DepositWindow = None
def on_deposit_button_clicked(connection, user_id):
    global DepositWindow

    try:
        if DepositWindow is None or not QtWidgets.QWidget.isVisible(DepositWindow):
            DepositWindow = QtWidgets.QDialog()
            deposit_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\deposit_amount.ui", DepositWindow)

            deposit_ui.deposit_final.clicked.connect(lambda: handle_deposit(deposit_ui, connection, user_id))

            DepositWindow.show()
        else:
            DepositWindow.activateWindow()
    except Exception as e:
        print(f"An error occurred: {e}")
        QMessageBox.warning(None, "Error", f"An error occurred while opening the deposit window: {e}")


def handle_deposit(deposit_ui, connection, user_id):
    try:
        deposit_amount_text = deposit_ui.findChild(QtWidgets.QLineEdit, "deposit_amount").text()

        # Validate if the input is an integer and less than 100000
        if not deposit_amount_text.isdigit() or int(deposit_amount_text) > 100000:
            QMessageBox.warning(deposit_ui, "Invalid Input", "Please enter a valid amount (integer and less than 100000).")
            return

        deposit_amount = int(deposit_amount_text)
        cursor = connection.cursor()

        # Fetch current balance
        cursor.execute("SELECT account_balance FROM Account WHERE user_id = ?", (user_id,))
        current_balance = cursor.fetchone()[0]

        # Update the new balance
        new_balance = current_balance + deposit_amount
        cursor.execute("UPDATE Account SET account_balance = ? WHERE user_id = ?", (new_balance, user_id))
        connection.commit()

        QMessageBox.information(deposit_ui, "Deposit Successful", "Your deposit was successful.")
        DepositWindow.close()

    except Exception as e:
        QMessageBox.warning(deposit_ui, "Error", f"An error occurred: {e}")


global TransferWindow
TransferWindow = None

def on_transfer_button_clicked(connection, user_id):
    global TransferWindow
    try:
        # Retrieve the user's account number using user_id
        cursor = connection.cursor()
        cursor.execute("SELECT account_no FROM Account WHERE user_id = ?", (user_id,))
        user_account_data = cursor.fetchone()
        cursor.close()

        if user_account_data:
            user_account_no = user_account_data[0]
            launch_transfer_ui(connection, user_id, user_account_no)
        else:
            QMessageBox.warning(None, "Error", "Your account number could not be found.")

    except Exception as e:
        QMessageBox.warning(None, "Error", f"An error occurred while retrieving the account number: {e}")

def launch_transfer_ui(connection, user_id, user_account_no):
    global TransferWindow

    if TransferWindow is None or not QtWidgets.QWidget.isVisible(TransferWindow):
        TransferWindow = QtWidgets.QDialog()
        transfer_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\transfer_amount.ui", TransferWindow)

        # Set up the transfer button click handling
        transfer_ui.findChild(QtWidgets.QPushButton, "transfer_final").clicked.connect(
            lambda: handle_transfer(transfer_ui, connection, user_id, user_account_no)
        )

        TransferWindow.show()
    else:
        TransferWindow.activateWindow()

def handle_transfer(transfer_ui, connection, user_id, user_account_no):
    transfer_account_no = transfer_ui.findChild(QtWidgets.QLineEdit, "transfer_account").text()
    transfer_amount_text = transfer_ui.findChild(QtWidgets.QLineEdit, "transfer_amount").text()

    try:
        # Convert transfer amount to float and check if it's a positive number
        transfer_amount = float(transfer_amount_text)
        if transfer_amount <= 0:
            QMessageBox.warning(transfer_ui, "Invalid Amount", "Please enter a positive number for the transfer amount.")
            return

        cursor = connection.cursor()

        # Check if the target account number exists and is different from the user's own account number
        cursor.execute("SELECT COUNT(*) FROM Account WHERE account_no = ?", (transfer_account_no,))
        account_exists = cursor.fetchone()[0]
        if account_exists == 0:
            QMessageBox.warning(transfer_ui, "Invalid Account", "The account number entered does not exist.")
            return
        elif transfer_account_no == user_account_no:
            QMessageBox.warning(transfer_ui, "Invalid Transfer", "Cannot transfer to the same account number.")
            return
        
        # Check if user has enough balance for the transfer
        cursor.execute("SELECT account_balance FROM Account WHERE account_no = ?", (user_account_no,))
        user_account_balance = cursor.fetchone()[0]
        if user_account_balance < transfer_amount:
            QMessageBox.warning(transfer_ui, "Insufficient Funds", "You do not have enough balance for this transfer.")
            return

        # Deduct the transfer amount from the user's account
        new_user_balance = user_account_balance - transfer_amount
        cursor.execute("UPDATE Account SET account_balance = ? WHERE account_no = ?", (new_user_balance, user_account_no))
        
        # Add the transfer amount to the recipient's account
        cursor.execute("SELECT account_balance FROM Account WHERE account_no = ?", (transfer_account_no,))
        recipient_account_balance = cursor.fetchone()[0]
        new_recipient_balance = recipient_account_balance + transfer_amount
        cursor.execute("UPDATE Account SET account_balance = ? WHERE account_no = ?", (new_recipient_balance, transfer_account_no))
        
        connection.commit()
        QMessageBox.information(transfer_ui, "Transfer Successful", "The transfer was successful.")
        TransferWindow.close()

    except ValueError:
        QMessageBox.warning(transfer_ui, "Invalid Input", "Please enter a valid number for the transfer amount.")
    except Exception as e:
        QMessageBox.warning(transfer_ui, "Transfer Failed", f"An error occurred during the transfer: {e}")
    finally:
        cursor.close()



global EmployeeManagementWindow
EmployeeManagementWindow = None

def launch_employee_management_ui(connection):
    global EmployeeManagementWindow
    if EmployeeManagementWindow is None or not QtWidgets.QWidget.isVisible(EmployeeManagementWindow):
        EmployeeManagementWindow = QtWidgets.QMainWindow()
        employee_management_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\employee_management.ui", EmployeeManagementWindow)
        
        # Assuming 'employeeTable' is the objectName of your QTableWidget in the UI.
        employee_table = employee_management_ui.findChild(QtWidgets.QTableWidget, "employee_table")

        # Set the table to select full rows instead of individual cells
        employee_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Now populate the table with employee data
        populate_employee_table(employee_table, connection)
        
        # Setup any buttons or fields you need here, for example:
        add_button = employee_management_ui.findChild(QtWidgets.QPushButton, "add")
        add_button.clicked.connect(lambda: on_add_employee_clicked(connection))

        # remove_button = employee_management_ui.findChild(QtWidgets.QPushButton, "remove")
        # remove_button.clicked.connect(lambda: on_remove_employee_clicked(employee_table, connection))

        EmployeeManagementWindow.show()
    else:
        EmployeeManagementWindow.activateWindow()

def populate_employee_table(employee_table, connection):
    try:
        cursor = connection.cursor()

        # Assuming the HR department has a specific department_id, for example, 'HR'
        # The actual ID should be the one used in your database
        hr_department_id = 'HR' # Replace with the actual department_id of HR in your database

        # SQL query to fetch all employees except those from the HR department
        cursor.execute("""
            SELECT employee_id, employee_first_name, employee_last_name, employee_email, department_id 
            FROM Employee 
            WHERE department_id != ?
        """, (hr_department_id,))
        employees = cursor.fetchall()

        # Set the number of rows in the table based on the number of employees
        employee_table.setRowCount(len(employees))

        # Populate the table
        for row_index, (employee_id, first_name, last_name, email, dept_id) in enumerate(employees):
            # Merge first and last name
            full_name = f"{first_name} {last_name}"

            # Set items in the table
            employee_table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(employee_id)))
            employee_table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(full_name))
            employee_table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(email))
            employee_table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(dept_id))

    except Exception as e:
        print(f"An error occurred while populating the employee table: {e}")
    finally:
        cursor.close()

global AddEmployeeWindow
AddEmployeeWindow = None
def on_add_employee_clicked(connection):
    global AddEmployeeWindow

    try:
        # Check if the AddEmployeeWindow is already open
        if AddEmployeeWindow is None or not QtWidgets.QWidget.isVisible(AddEmployeeWindow):
            AddEmployeeWindow = QtWidgets.QDialog()
            add_employee_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\add_employee.ui", AddEmployeeWindow)

            # Connect the submit button's click signal to the function that will handle the new employee creation
            submit_button = add_employee_ui.findChild(QtWidgets.QPushButton, "apply")  # Make sure 'apply' is the correct objectName of your submit button in the UI
            submit_button.clicked.connect(lambda: add_new_employee_to_db(add_employee_ui, connection))

            AddEmployeeWindow.show()
        else:
            AddEmployeeWindow.activateWindow()

    except Exception as e:
        print(f"An error occurred while launching the Add Employee window: {e}")
        QMessageBox.critical(None, "Error", f"An error occurred while launching the Add Employee window: {e}")




def add_new_employee_to_db(add_employee_ui, connection):
    # Get the values from the UI
    first_name = add_employee_ui.findChild(QtWidgets.QLineEdit, "first_name").text()
    last_name = add_employee_ui.findChild(QtWidgets.QLineEdit, "last_name").text()
    number = add_employee_ui.findChild(QtWidgets.QLineEdit, "number").text()
    dob = add_employee_ui.findChild(QtWidgets.QLineEdit, "dob").text()
    email = add_employee_ui.findChild(QtWidgets.QLineEdit, "email").text()
    password = add_employee_ui.findChild(QtWidgets.QLineEdit, "pass").text()  
    dept_id = add_employee_ui.findChild(QtWidgets.QComboBox, "deptid").currentText()

    # Calculate age from dob
    birth_date = datetime.strptime(dob, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    # Determine department table
    department_tables = {
        'IM': 'Investment_Manager',
        'A': 'Accountant',
        'CS': 'Customer_Service_Representative'
    }
    department_table = department_tables.get(dept_id)

    if department_table is None:
        print(f"No table found for department ID: {dept_id}")
        return

    # Start database operations
    cursor = connection.cursor()
    try:
        # Check if email already exists
        cursor.execute("SELECT COUNT(*) FROM Employee WHERE employee_email = ?", (email,))
        if cursor.fetchone()[0] > 0:
            print("Email already exists.")
            QMessageBox.warning(add_employee_ui, "Error", "The email address already exists in the system.")
            return

        # Insert into Employee table
        cursor.execute("""
            INSERT INTO Employee (employee_first_name, employee_last_name, employee_email, 
                                  employee_number, employee_dob, department_id, employee_age)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, number, dob, dept_id, age))

        # Get the ID of the new employee
        new_employee_id = cursor.execute("SELECT @@IDENTITY").fetchval()

        # Insert into the corresponding department table
        cursor.execute(f"""
            INSERT INTO {department_table} (employee_id, employee_email, employee_password)
            VALUES (?, ?, ?)
        """, (new_employee_id, email, password))

        # Commit the transaction
        connection.commit()
        QMessageBox.information(add_employee_ui, "Success", "New employee added successfully.")

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        QMessageBox.critical(add_employee_ui, "Error", f"An error occurred while adding the new employee: {e}")
    finally:
        cursor.close()


# def on_remove_employee_clicked(employee_table, connection):
#     selected_row = employee_table.currentRow()
#     if selected_row == -1:
#         QMessageBox.warning(employee_table, "Selection Error", "Please select an entire row to remove an employee.")
#         return

#     employee_id_item = employee_table.item(selected_row, 0)
#     department_id_item = employee_table.item(selected_row, 3)

#     if not employee_id_item or not department_id_item:
#         QMessageBox.warning(employee_table, "Selection Error", "Please select a valid row with an employee ID and department.")
#         return

#     employee_id = employee_id_item.text()
#     department_id = department_id_item.text()

#     department_tables = {
#         'A': 'accountant',
#         'IM': 'investment_manager',
#         'CS': 'customer_service_representative',
#         # Add more mappings as needed
#     }
#     department_table = department_tables.get(department_id)

#     cursor = connection.cursor()
#     try:
#         cursor.execute("BEGIN TRANSACTION;")

#         if department_table:
#             cursor.execute(f"DELETE FROM {department_table} WHERE employee_id = ?", (employee_id,))
        
#         cursor.execute("DELETE FROM Employee WHERE employee_id = ?", (employee_id,))

#         if cursor.rowcount == 0:
#             cursor.execute("ROLLBACK;")
#             QMessageBox.warning(employee_table, "Error", "No employee found with the given ID.")
#         else:
#             cursor.execute("COMMIT;")
#             QMessageBox.information(employee_table, "Success", "The employee has been removed successfully.")
#             employee_table.removeRow(selected_row)

#     except pyodbc.Error as e:
#         error_msg = e.args[1]  # Error message from the pyodbc exception
#         QMessageBox.critical(employee_table, "Database Error", f"An error occurred while removing the employee: {error_msg}")
#         cursor.execute("ROLLBACK;")  # Rollback the transaction
#         print(f"Database error: {error_msg}")
#     except Exception as e:
#         QMessageBox.critical(employee_table, "Error", f"An error occurred: {e}")
#         cursor.execute("ROLLBACK;")  # Rollback the transaction
#     finally:
#         cursor.close()

global BalanceSheetWindow
BalanceSheetWindow = None
def launch_balance_sheet_ui(connection):
    global BalanceSheetWindow

    # Load the UI file for the balance sheetz
    BalanceSheetWindow = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\balance_sheet.ui")
    
    # Retrieve and display the total savings account balance
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(saving_account_balance) FROM interest_type")
    savings_total = cursor.fetchone()[0]
    BalanceSheetWindow.findChild(QtWidgets.QLineEdit, "saving_total").setText(str(savings_total))
    
    # Retrieve and display the total amount loaned for 'due' and 'late' loans
    cursor.execute("SELECT SUM(Amount_Loaned) FROM Loan WHERE Loan_Status IN ('due', 'late')")
    loans_total = cursor.fetchone()[0]
    BalanceSheetWindow.findChild(QtWidgets.QLineEdit, "loan_total").setText(str(loans_total))

    # Connect the calculate button to the function that computes and shows profit or loss
    calculate_button = BalanceSheetWindow.findChild(QtWidgets.QPushButton, "calculate")
    calculate_button.clicked.connect(lambda: calculate_profit_loss(BalanceSheetWindow, connection))

    # Show the balance sheet window
    BalanceSheetWindow.show()

def calculate_profit_loss(window, connection):
    # Retrieve user inputs
    funds = float(window.findChild(QtWidgets.QLineEdit, "funds").text() or 0)
    saving_total = float(window.findChild(QtWidgets.QLineEdit, "saving_total").text() or 0)
    priors = float(window.findChild(QtWidgets.QLineEdit, "priors").text() or 0)
    cost = float(window.findChild(QtWidgets.QLineEdit, "cost").text() or 0)
    loan_total = float(window.findChild(QtWidgets.QLineEdit, "loan_total").text() or 0)
    salary = float(window.findChild(QtWidgets.QLineEdit, "salary").text() or 0)

    # Calculate profit or loss
    profit_loss = funds + saving_total + priors - cost - loan_total - salary

    # Determine if it's a profit or loss and show corresponding message box
    if profit_loss > 0:
        QMessageBox.information(window, "Profit Calculation", f"The profit for this year is: {profit_loss}")
    elif profit_loss < 0:
        QMessageBox.warning(window, "Loss Calculation", f"The loss for this year is: {profit_loss}")
    else:
        QMessageBox.information(window, "Break Even", "The company has broken even this year.")



# Now, update the initial_ui function to pass the FirstWindow instance
def launch_initial_ui(connection):
    app = QtWidgets.QApplication(sys.argv)
    FirstWindow = QtWidgets.QMainWindow()
    first_ui = uic.loadUi(r"C:\Users\qazim\OneDrive\Desktop\database bank_managment_system_folder\select_login_type.ui", FirstWindow)

    # Connect the admin login button to launch the employee login and close the first window
    first_ui.login_button_admin.clicked.connect(lambda: [FirstWindow.close(), launch_employee_login_ui(connection, FirstWindow)])
    
    # Connect the customer login button to launch the customer login and close the first window
    first_ui.login_button_customer.clicked.connect(lambda: [FirstWindow.close(), launch_customer_login_ui(connection)])

    FirstWindow.show()
    sys.exit(app.exec())



if __name__ == '__main__':
    connection = connect_to_database()
    if connection:
        launch_initial_ui(connection)
    else:
        print("Failed to connect to the database.")

