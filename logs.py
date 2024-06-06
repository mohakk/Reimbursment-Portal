import mysql.connector

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="7587061048@Mg",
    database="reimbursement_db"
)

cursor = conn.cursor()


cursor.execute("SELECT * FROM audit_log")
logs = cursor.fetchall()

cursor.close()
conn.close()

with open("logs.txt", "w") as file:
    for log in logs:
        file.write(str(log) + "\n")
