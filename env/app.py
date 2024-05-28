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
    if not "email" in session:
        print('sjdibksd')
        return render_template("home.html", message='Please Login')
    else:
        if request.method=="POST":
            keywords=request.form["keywords"]
            experience=request.form["experience"]
            location=request.form["location"]
            counter = request.form['counter']
            if(len(counter) == 0):
                counter = '0'
            [linkedIn_result,counter] = await scraper.scrapeLinkedin(keywords,location,counter) 
            [naukri_result,counter] = await scraper.scrapeNaukri(keywords,location,counter) 
            # [console_result,counter] = [[{'title': 'Business Analyst', 'location': 'Chennai, Tamil Nadu, India', 'company': 'HTC Global Services', 'desc': 'Education: Bachelor’s degree in Computer Science, Information Systems, or Finance• Role Specific Experience: 3+ years of relevant technical and business work experience• Banking & Financial domain experience, along with knowledge of risk management, familiarity with concepts of finance and accounting• Proficiency in MS Excel• Experience in defining and implementing technology solutions for a major financial institution• Extensive experience as a Business Analyst for a large financial institution • Extensive experience in gathering business requirements and developing functional specifications with special emphasis on use cases, defining test cases, and providing user training and support• Extensive experience with various system development lifecycle methodologies and tailoring the artifacts to those methodologies• Solution-oriented, detailed-focused, showing strong analytical and organization skills• Familiarity with relational databases / RDMS• Experience with writing simple SQL statements (mostly SELECT – with aim to analyze datasets)• Familiarity with any object-oriented programming language is a plus (c# preferred)', 'link': 'https://in.linkedin.com/jobs/view/business-analyst-at-htc-global-services-3881422508?position=17&pageNum=0&refId=z4jy4%2FbFvjbbFvUEJfE14g%3D%3D&trackingId=%2B1u09zq6ZmGQCjkggRemFw%3D%3D&trk=public_jobs_jserp-result_search-card'}],60]
            console_result = linkedIn_result + naukri_result
            return render_template("jobpg.html", console_result = console_result, counter = counter, keywords= keywords, location = location)
        else:
            return render_template("jobpg.html") 


if __name__ == '__main__':
    print('starts')
    app.run(debug=True)
