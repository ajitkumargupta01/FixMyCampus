import mysql.connector
import datetime

# def get_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Vikash@123",
#         database="fmp"
#     )

# def get_connection():  # My database
#     return mysql.connector.connect(
#         host = "sql12.freesqldatabase.com",
#         database = "sql12773714",
#         username = "sql12773714",
#         password = "ML3VxVa9L2"
#     )

def get_connection(): #ajit's database
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12774989",
        password="acxEkHFzcu",
        database="sql12774989"
    )


def create_Table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            first_name VARCHAR(20),
            last_name VARCHAR(20),
            email VARCHAR(100),
            password VARCHAR(100),
            mob_num VARCHAR(15),
            gender VARCHAR(10),
            roll_no VARCHAR(15) PRIMARY KEY,
            is_banned BOOLEAN DEFAULT FALSE
        )
    ''')    
    conn.commit()
    conn.close()

def fetch_user(roll_no):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT first_name, last_name, email, mob_num, gender, roll_no,is_banned FROM users WHERE roll_no = %s", (roll_no,))
        user = cur.fetchone()
        return user
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        conn.close()




def register_user(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (first_name, last_name, email, password, mob_num, gender, roll_no)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    conn.close()

def check_user(roll_no, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE roll_no=%s AND password=%s", (roll_no, password))
    data = cursor.fetchone()
    cursor.execute("SELECT is_banned FROM users WHERE roll_no=%s",(roll_no,))
    status = cursor.fetchone()
    return (data,status)

def forgot_password(roll_no, mob_num, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = %s WHERE roll_no = %s AND mob_num = %s",
        (password, roll_no, mob_num)
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()
    return updated_rows > 0

def update_user(roll_no, first_name, last_name, email, mob_num, gender):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE users
            SET first_name = %s,
                last_name = %s,
                email = %s,
                mob_num = %s,
                gender = %s
            WHERE roll_no = %s
        ''', (first_name, last_name, email, mob_num, gender, roll_no))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False

def create_issues_table():
    conn = get_connection()
    cur = conn.cursor()

    #ALTER TABLE issues AUTO_INCREMENT = 43290;
    cur.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            roll_no VARCHAR(15),
            issue_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
            issue_type  VARCHAR(15),
            description VARCHAR(1000),
            location VARCHAR(50),
            status VARCHAR(50),
            date_reported VARCHAR(50)
        )
    """)
    conn.commit()
    conn.close()
    
def add_issue(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO issues (roll_no,issue_type,description,location,status,date_reported) VALUES(%s,%s,%s,%s,%s,%s)
    """,data)
    conn.commit()
    conn.close()


def view_my_issue(roll_no):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT * FROM issues WHERE roll_no = '{roll_no}'
    """)
    data = cur.fetchall()
    conn.close()
    return data

def view_all_issue():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM issues")
    data = cur.fetchall()
    conn.close()
    return data

def verify_and_update_password(roll_no, current_password, new_password):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE roll_no = %s", (roll_no,))
            result = cur.fetchone()
            if result is None or result[0] != current_password:
                return False

            cur.execute("UPDATE users SET password = %s WHERE roll_no = %s", (new_password, roll_no))
            conn.commit()
            return True
    except Exception as e:
        print(f"[Password Update] Error: {e}")
        return False
    finally:
        conn.close()

#----------------------------------------------------------------------------------------------

# ------------------ Issue Management ------------------

def view_all_issue():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT roll_no, issue_id, issue_type, description, location, status, date_reported FROM issues")
    data = cur.fetchall()
    conn.close()
    return data

def update_issue_status(issue_id, new_status):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE issues SET status = %s WHERE issue_id = %s", (new_status, issue_id))
        conn.commit()
        conn.close()
        log_action("Issue Updated", f"Issue ID: {issue_id}, New Status: {new_status}")
        return True
    except Exception as e:
        print(f"[Update Issue] Error: {e}")
        return False

def delete_issue(issue_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM issues WHERE issue_id = %s", (issue_id,))
        conn.commit()
        conn.close()
        log_action("Issue Deleted", f"Issue ID: {issue_id}")
        return True
    except Exception as e:
        print(f"[Delete Issue] Error: {e}")
        return False

def search_issues(status=None, category=None, roll_no=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT roll_no, issue_id, issue_type, description, location, status, date_reported FROM issues WHERE 1=1"
    params = []

    if status:
        query += " AND status = %s"
        params.append(status)
    if category:
        query += " AND issue_type LIKE %s"
        params.append(f"%{category}%")
    if roll_no:
        query += " AND roll_no LIKE %s"
        params.append(f"%{roll_no}%")

    cur.execute(query, tuple(params))
    data = cur.fetchall()
    conn.close()
    return data

# ------------------ User Management ------------------

def all_user():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT first_name, last_name, email, password, mob_num, gender, roll_no FROM users")
    users = cur.fetchall()
    conn.close()
    return users

def delete_user_by_roll(roll_no):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE roll_no = %s", (roll_no,))
        conn.commit()
        conn.close()
        log_action("User Deleted", f"Roll No: {roll_no}")
        return True
    except Exception as e:
        print(f"[Delete User] Error: {e}")
        return False

def reset_user_password(roll_no, new_password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = %s WHERE roll_no = %s", (new_password, roll_no))
        conn.commit()
        conn.close()
        log_action("Password Reset", f"Roll No: {roll_no}")
        return True
    except Exception as e:
        # print(f"[Reset Password] Error: {e}")
        return False

# ------------------ Simulated Ban/Unban Using Logs ------------------
#---------- create Audit logs table--------------------
def create_audit_logs_table():
    try:
        # Establish the connection to your database
        connection = get_connection()
        
        cursor = connection.cursor()
        
        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            action VARCHAR(255),
            details TEXT,
            timestamp DATETIME
        );
        """
        
        cursor.execute(create_table_query)
        connection.commit()
    
    except mysql.connector.Error as err:
        pass
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

#------------------- saving log action ------------------
def log_action(action, detail):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO audit_logs (action, details, timestamp) VALUES (%s, %s, %s)",
                    (action, detail, datetime.datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Audit Log] Error: {e}")

def ban_user(roll_no):
    try:
        log_action("User Banned", f"Roll No: {roll_no}")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET is_banned=1 WHERE roll_no=%s",(roll_no,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # print(f"[Ban User] Error: {e}")
        return False

def unban_user(roll_no):
    try:
        log_action("User Unbanned", f"Roll No: {roll_no}")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET is_banned=0 WHERE roll_no=%s",(roll_no,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # print(f"[Unban User] Error: {e}")
        return False


def get_banned_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT roll_no,first_name,last_name FROM users WHERE is_banned = 1")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_banned_users_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT first_name, last_name, email, password, mob_num, gender, roll_no FROM users WHERE is_banned=1")
    rows = cur.fetchall()
    conn.close()
    return rows
# ------------------ Audit Logs ------------------


def get_audit_logs(limit=50):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, action, details, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
        logs = cur.fetchall()
        conn.close()
        return logs
    except Exception as e:
        # print(f"[Get Logs] Error: {e}")
        return []




            
            
def delete_issue(issue_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        delete_query = "DELETE FROM issues WHERE issue_id = %s"  # Use 'issue_id' instead of 'id'
        cursor.execute(delete_query, (issue_id,))
        connection.commit()
        return cursor.rowcount > 0  # Returns True if a row was deleted
    except mysql.connector.Error as err:
        print(f"[Delete Issue] Error: {err}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def search_issues(status=None, category=None, roll_no=None, issue_id=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT roll_no, issue_id, issue_type, description, location, status, date_reported FROM issues WHERE 1=1"
    params = []

    if status:
        query += " AND status = %s"
        params.append(status)
    if category:
        query += " AND issue_type LIKE %s"
        params.append(f"%{category}%")
    if roll_no:
        query += " AND roll_no LIKE %s"
        params.append(f"%{roll_no}%")
    if issue_id:
        query += " AND issue_id = %s"
        params.append(issue_id)

    cur.execute(query, tuple(params))
    data = cur.fetchall()
    conn.close()
    return data
