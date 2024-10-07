from flask import Flask, render_template, request, redirect, url_for,session, flash, jsonify, send_file
from flask_pymongo import PyMongo
import pandas as pd
import Regression
import matplotlib.pyplot as plt

ed = {
    'Unknown': 0,
    'High School': 1,
    "Bachelor's": 2,
    "Bachelor's Degree": 3,
    "Master's": 4,
    "Master's Degree": 5,
    'PhD': 6,
    'phD': 7
}

app = Flask(__name__)

app.config["SECRET_KEY"] = "xYzAbC"

app.config["MONGO_URI"] = "mongodb+srv://vanirudha95:fds_project@fdsproject.2l2ya.mongodb.net/"
mongo1 = PyMongo(app, uri = "mongodb+srv://vanirudha95:fds_project@fdsproject.2l2ya.mongodb.net/sample")

all_models = Regression.load_models()
Regression.standardize()
print("successfull")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle Sign In logic here

        email = request.form.get("signin-email")
        password = request.form.get("signin-password")
        session['email'] = email
        # Check if user exists and password matches
        user = mongo1.db.user_data.find_one({"email": email})
        is_admin = user.get('is_admin')
        session['is_admin'] = is_admin
        if user and user["pass"] == password:
            # Successful login logic (redirect to dashboard, etc.)
            print("Signed in")
            return redirect(url_for("home_page"))
        else:
            return render_template('login.html', result_message="Invalid email or password.")

    return render_template('login.html')


@app.route("/signup", methods=["POST", "GET"])
def signup():
    result_message = None  # Initialize the message variable

    if request.method == "POST":
        email = request.form.get("signup-email")
        if mongo1.db.user_data.find_one({"email": email}):
            result_message = "Account with the same Email-ID already exists."
            return render_template('signup.html', result_message=result_message)  # Return to login with message
        else:
            name = request.form.get("signup-name")
            password = request.form.get("signup-password")  # Use the correct field name
            mongo1.db.user_data.insert_one({"email": email, "user": name, "pass": password})  # Use insert_one
            result_message = "Account created successfully!"
            return redirect(url_for("login"))  # Return to login with success message

    return render_template('signup.html', result_message=result_message)


@app.route("/homepage", methods = ["POST", "GET"])
def home_page():
    return render_template("home_page.html", is_admin = session.get('is_admin'))  # Placeholder for your dashboard

@app.route("/salary_predictor", methods = ["POST", "GET"])
def salary_predictor():

    if request.method == "POST":
        print("i am here")
        email = session.get('email')
        age = request.form.get("age")
        gender = request.form.get("gender")
        ed_lvl = request.form.get("education")
        yoe = request.form.get("experience")
        job_role = request.form.get("job-role") 
        job_title = request.form.get("job-title")
        mongo1.db.applicants.insert_one({"email": email, "age": age, "gender": gender, "education": ed_lvl, "yoe": yoe,
                                         "Job_Role": job_role, "Job_Title": job_title})
        if gender == "Male":
            num_gender = 1
        else:
            num_gender = 0

        new_ed_lvl = ed[ed_lvl]
        data = {
            "Age" : age,
            "Gender" : num_gender,
            "Years of Experience" : yoe,
            "Job Title": job_title,
            "Education Level Standardized" : new_ed_lvl
        }
        x_test = pd.DataFrame(data, index=[0])
        y_predict = Regression.predictor(all_models, x_test)
        final_img = Regression.plotter(y_predict)

        img_url = f"{url_for('static', filename='salary_plot.png')}"
        plt.savefig('static/salary_plot.png')

        return render_template('salary_predictor.html', img_url=img_url)
    else:
        print("i not am here")
        return render_template("salary_predictor.html")

@app.route("/admin", methods = ["POST", "GET"])
def admin():
    if session.get('is_admin'):
        print("anirudh")
        return render_template("admin.html")
    else:
        flash("YOU ARE NOT ADMIN", "error")
        return redirect(request.referrer)

@app.route("/add_remove",methods = ["POST", "GET"])
def add_remove():
     # Assuming you have a collection named 'users'
    users_collection = mongo1.db.applicants
    
    # Fetching all documents from the 'users' collection
    users = users_collection.find()

    # Convert MongoDB documents to a list of dictionaries and serialize the _id
    user_list = []
    for user in users:
        user_data = {
            "id": str(user['_id']),  # Convert ObjectId to string
            "email": user.get('email', ''),
            "age": user.get('age', ''),
            "gender": user.get('gender', ''),
            "education": user.get('education', ''),
            "yearsOfExperience": user.get('yoe', ''),
            "jobRole": user.get('Job_Role', ''),
            "jobTitle": user.get('Job_Title', '')
        }
        user_list.append(user_data)
    return render_template("add_remove.html", users = user_list)
    
def access_display():
    status = mongo1.db.user_data.find()
    user_status = []
    for user in status:
        user_data = {
            "email": user.get('email', ''),
            "is_admin": user.get('is_admin', '')
        }
        user_status.append(user_data)

    return render_template("access.html", users=user_status)

@app.route("/access", methods = ["POST","GET"])
def access():
    if request.method == "POST":
        user_changes = request.form.getlist("user_ids")
        for user_email in user_changes:
            is_admin_name = f'is_admin_{user_email}'
            is_admin = is_admin_name in request.form

            mongo1.db.user_data.update_one(
                {'email': user_email},
                {'$set': {'is_admin': is_admin}}
            )

        return access_display()
    else:
        return access_display()

if __name__ == "__main__":
    app.run(debug=True)
