from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import os

application = app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'leave_management'

mysql = MySQL(app)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("select e_id,manager from employee where username='{}' and password='{}'".format(username, password))
    result = cur.fetchall()
    if len(result) == 0:
        ret_dict = {"error": "username or password doesn't match"}
        return ret_dict
    else:
        session['e_id'] = result[0][0]
        session['manager'] = result[0][1]
        ret_dict = {}
        ret_dict["e_id"] = result[0][0]
        ret_dict["manager"] = result[0][1]
        return ret_dict


@app.route('/register', methods=['POST'])
def add_employee():
    try:
        e_name = request.form['e_name']
        username = request.form['username']
        password = request.form['password']
        manager = request.form['manager']
        casual_leaves = 7
        sick_leaves = 7
        earned_leaves = 14
        cur = mysql.connection.cursor()
        cur.execute(
            "insert into employee(e_name,username,password,casual_leaves,sick_leaves,earned_leaves,manager) values ('{}','{}','{}',{},{},{})".format(
                e_name, username, password, casual_leaves, sick_leaves, earned_leaves, manager))
        cur.connection.commit()
        ret_dict = {}
        ret_dict['message'] = "Registration Successful"
        return ret_dict
    except:
        ret_dict = {}
        ret_dict['error'] = "Some error occurred"
        return ret_dict


@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    try:
        leave_dict = {"Casual Leaves": "casual_leaves", "Sick Leaves": "sick_leaves", "Earned Leaves": "earned_leaves"}
        leave_type = leave_dict[request.form['leave_type']]
        days = int(request.form['days'])
        if leave_type == "casual_leaves" and days > 3:
            ret_dict = {}
            ret_dict['error'] = "Casual Leaves can't be greater than 3"
            return ret_dict
        if leave_type == "earned_leaves" and days < 3:
            ret_dict = {}
            ret_dict['error'] = "Earned Leaves can't be lesser than 3"
            return ret_dict
        cur = mysql.connection.cursor()
        cur.execute("select {} from employee where e_id={}".format(leave_type, session['e_id']))
        leaves = cur.fetchall()[0][0]
        if leaves > days:
            leaves_left = leaves - days
            cur.execute("update employee set {}={} where e_id={}".format(leave_type, leaves_left, session['e_id']))
            cur.connection.commit()
            ret_dict = {}
            ret_dict['message'] = "Applied for {} days leave, {} leaves left".format(days, leaves_left)
            return ret_dict
        else:
            ret_dict = {}
            ret_dict['error'] = "Can't be allowed to take these many holidays"
            return ret_dict
    except:
        ret_dict = {}
        ret_dict['error'] = "Some error occurred"
        return ret_dict

@app.route('approve_leave',methods=['GET'])
def approve_leave():
    if session['manager']==1:
        e_id=request.args.get('e_id')
        leave_type=request.args.get('leave_type')
        days=request.args.get('days')
        status=int(request.args.get('status'))
        if status==1:
            ret_dict = {}
            ret_dict['message'] = "Leave Denied"
            return ret_dict
        else:
            cur=mysql.connection.cursor()
            cur.execute("select {} from employee where e_id={}".format(leave_type,e_id))
            leaves_left=cur.fetchall()[0][0]
            leaves_left+=days
            cur.execute("update employee set {}={} where e_id={}".format(leave_type,leaves_left,e_id))
            cur.connection.commit()
            ret_dict = {}
            ret_dict['message'] = "Leave Approved"
            return ret_dict
    else:
        ret_dict = {}
        ret_dict['error'] = "Only managers are allowed to approve leaves"
        return ret_dict

if __name__ == "__main__":
    app.run(debug=True)
