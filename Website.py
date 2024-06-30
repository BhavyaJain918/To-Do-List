import os
import pymysql
import datetime
from flask import Flask , flash , redirect , render_template , request , make_response

app = Flask(__name__ , template_folder = "" , static_folder = "")
app.secret_key = "My_Secret_Project"

mydb = pymysql.connect(host = "" , user = "" , passwd = "" , database = "List")  # Use host as 'localhost'
cursor = mydb.cursor()

@ app.route('/')
def base():
    resp = make_response(render_template("Base.html"))
    resp.headers["Cache-Control"] = "no-store"
    return resp

@ app.route("/about")
def about():
    return (render_template("About.html"))

@ app.route("/employee")
def employee():
    return (render_template("Employee.html"))

@ app.route("/contactus")
def contactus():
    return (render_template("Contact.html"))

@ app.route("/register" , methods = ["POST" , "GET"])
def register():
    if request.method == "POST":
        try:
            global user
            user = request.form.get("username")
            passwd = request.form.get("password")
            cursor.execute("INSERT INTO User VALUES(%s , %s)" , (user , passwd))
            mydb.commit()
            return (redirect("/list"))
        except OSError:
            flash("Error Occurred" , "error")
        except pymysql.IntegrityError:
            flash("User Already Registered" , "error")
    return (render_template("Register.html"))

@ app.route("/login" , methods = ["POST" , "GET"])
def login():
    if request.method == "POST":
        try:
            global user
            user = request.form.get("username")
            passwd = request.form.get("password")
            cursor.execute("SELECT Password FROM User WHERE Name = (%s)" , (user , ))
            res = cursor.fetchone()
            if res != None:
                for result in res:
                    cursor.execute("SELECT Name FROM User WHERE Password = (%s)" , (str(result) , ))
                    user_var = cursor.fetchone()
                    if user_var != None:
                        for username in user_var:
                            if str(result) == passwd and str(username) == user:
                                return (redirect("/list"))
                            else:
                                flash("No Data Found" , "error")
                    else:
                        flash("No Data Found" , "error")
            else:
                flash("Enter Valid Values" , "error")
        except OSError:
            flash("Error Occurred" , "error")
        except pymysql.InternalError:
            flash("Error Occurred" , "info")
    return render_template("Login.html")

@ app.route("/list" , methods = ["POST" , "GET"])
def list():
    if request.method == "POST":
        text = request.form.get("task")
        if text != None:
            try:
                cursor.execute("INSERT INTO Task VALUES(%s , %s , %s , %s)" , (user , text.strip() , "Pending" , datetime.date.today()))
                mydb.commit()
            except pymysql.IntegrityError:
                pass
        cursor.execute("SELECT Task , Status , Date FROM Task WHERE Name = %s" , (user , ))     
        data = cursor.fetchall()
        resp = make_response(render_template("List.html" , data = data))
        resp.headers["Cache-Control"] = "no-store"
        return resp
    else:
        try:
            cursor.execute("SELECT Task , Status , Date FROM Task WHERE Name = %s" , (user , ))
            mydata = cursor.fetchall()
            resp = make_response(render_template("List.html" , data = mydata))
            resp.headers["Cache-Control"] = "no-store"
            return resp
        except NameError:
            return (redirect("/"))
    
@ app.route("/remove" , methods = ["POST" , "GET"])
def remove():
    if request.method == "POST":
        tasks = request.get_json()
        for task in tasks:
            if task["task"] != None: 
                cursor.execute("DELETE FROM Task WHERE Task = %s AND Name = %s" , (str(task["task"]).strip() , user))
                mydb.commit() 
        return (redirect("/list"))
    else:
        try:
            cursor.execute("SELECT Task , Status , Date FROM Task WHERE Name = %s" , (user , ))
            mydata_com = cursor.fetchall()
            resp = make_response(render_template("Remove.html" , data = mydata_com))
            resp.headers["Cache-Control"] = "no-store"
            return resp
        except NameError:
            return (redirect("/"))

@ app.route("/completed" , methods = ["POST" , "GET"])
def completed():
    if request.method == "POST":
        tasks = request.get_json()
        for task in tasks:
            if task["task"] != None: 
                cursor.execute("UPDATE Task SET Status = 'Completed' WHERE Task = %s AND Name = %s" , (str(task["task"]).strip() , user))
                mydb.commit() 
        return (redirect("/list"))
    else:
        cursor.execute("SELECT Task , Status , Date FROM Task WHERE Name = %s" , (user , ))
        mydata_com = cursor.fetchall()
        resp = make_response(render_template("Fini.html" , data = mydata_com))
        resp.headers["Cache-Control"] = "no-store"
        return resp

if __name__ == "__main__":
    app.run(host = "0.0.0.0" , port = int(os.environ.get("PORT" , 8080)) , debug = False)