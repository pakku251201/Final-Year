from flask import Flask, redirect, render_template, session, url_for, request, send_file
import psycopg2
import asyncio
import scraper

app = Flask(__name__) 
app.secret_key = "something"

hostname = 'localhost'
database ='pratheek'
username = 'pakku'
pwd = 'root'
port_id = 5300

def execute_query(query, values=None):
    conn = None
    try:
        conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
        cursor = conn.cursor()
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        if query.strip().split()[0].lower() == 'select':
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return True
    except psycopg2.Error as e:
        print("Error:", e)
        return False
    finally:
        if conn is not None:
            conn.close()

def create_user(email, password):
    query = "INSERT INTO users (email, password) VALUES (%s, %s)"
    return execute_query(query, (email, password))

def get_user(email):
    query = "SELECT * FROM users WHERE email = %s"
    result = execute_query(query, (email,))
    if result:
        return result[0]  # Return the first user found
    else:
        return None

create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
"""

execute_query(create_table_query)

@app.route("/")
def homepg():
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if create_user(email, password):
            return redirect(url_for("login"))
        else:
            return "Failed to register user"
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = get_user(email)
        if user and user[2] == password:
            session["email"] = email
            return redirect(url_for("jobpg"))
        else:
            return "Invalid email or password"
    return render_template("login.html")

@app.route("/jobpg", methods=['POST', 'GET'])
async def jobpg():
    print('comes here', request.method)
    if not "email" in session:
        return redirect(url_for("home.html"))
    else:
        if request.method=="POST":
            keywords=request.form["keywords"]
            experience=request.form["experience"]
            location=request.form["location"]
            console_result = await scraper.scrapeLinkedin(keywords,location) 
            return render_template("jobpg.html", console_result = console_result)
        else:
            return render_template("jobpg.html") 

@app.route("/download")
def download():
    file_path = f"{inputJobTitle}_{inputJobLocation}_jobs.xlsx"
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
