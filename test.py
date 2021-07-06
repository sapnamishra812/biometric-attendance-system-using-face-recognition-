import pymysql.connections

###Connect to the database
connection = pymysql.connect(host='localhost',user='root',password='',db='safr')
print("connect successful!!")
cursor = connection.cursor()
# db_sql = """CREATE DATABASE IF NOT EXISTS SAFR;"""

# table_sql = """CREATE TABLE IF NOT EXISTS Reg_Students (
#     Student_ID varchar(100) NOT NULL,
#     NAME varchar(100) NOT NULL,
#     DATE varchar(20) NOT NULL,
#     Registration_Time varchar(20) NOT NULL,
#     PRIMARY KEY (Student_ID)
# );
#    """

values = ('789',)
login_sql = 'SELECT * FROM reg_students WHERE Student_ID = % s'
cursor.execute(login_sql, values)
account = cursor.fetchone()
account = list(account)
print(account)
connection.commit()

# data = ("120","Aditi","15","20")
# insert_sql = ("INSERT INTO Register_Students(Student_ID,NAME,Date,Registration_Time) VALUES (%s, %s, %s, %s)")
# cursor.execute(db_sql,data)
# connection.commit()