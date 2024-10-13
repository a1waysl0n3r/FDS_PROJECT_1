from flask import Flask, render_template, request, redirect, url_for,session, flash, jsonify, send_file
from flask_pymongo import PyMongo
import pandas as pd
import Regression
import matplotlib.pyplot as plt
from bson import ObjectId
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

reverse_ed = {
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
mongo2 = PyMongo(app, uri = "mongodb://localhost:27017/Company")
all_models = Regression.load_models()
Regression.standardize()
print("successfull")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("signin-email")
        password = request.form.get("signin-password")
        session['email'] = email
        # Check if user exists and password matches
        user = mongo1.db.user_data.find_one({"email": email})
        is_admin = user.get('is_admin')
        session['is_admin'] = is_admin
        if is_admin:
            company = mongo1.db.admin.find_one({"email": email})
            session['company'] = company.get('company')
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

    action = request.form.get('action')
    print("i am here")
    email = session.get('email')
    age = request.form.get("age")
    gender = request.form.get("gender")
    ed_lvl = request.form.get("education")
    yoe = request.form.get("experience")
    job_role = request.form.get("job-role")
    job_title = request.form.get("job-title")
    if action == 'submit':
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
    elif action == 'submit_add':
        mongo1.db.applicants.insert_one(
            {"email": email, "Age": age, "Gender": gender, "Education Level": ed_lvl, "Years of Experience": yoe,
             "Job Role": job_role, "Job Title": job_title})

        return render_template('salary_predictor.html')
    else:
        return render_template('salary_predictor.html')


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
    company = session.get('company')
    db_company = f"applicants_company_{company}"
    users_collection = mongo1.db[db_company]
    
    # Fetching all documents from the 'users' collection
    users = users_collection.find()

    # Convert MongoDB documents to a list of dictionaries and serialize the _id
    user_list = []
    for user in users:
        user_data = {
            "id": str(user['_id']),  # Convert ObjectId to string
            "email": user.get('email', ''),
            "age": user.get('Age', ''),
            "gender": user.get('Gender', ''),
            "education": user.get('Education Level', ''),
            "yearsOfExperience": user.get('Years of Experience', ''),
            "jobRole": user.get('Job Role', ''),
            "jobTitle": user.get('Job Title', '')
        }
        user_list.append(user_data)
    return render_template("add_remove.html", users = user_list)

@app.route("/add-to-company", methods = ["POST", "GET"])
def add_application():
    if request.method == "POST":
        company = session.get('company')
        id = request.form.get("user_id")
        salary = request.form.get('salary')
        print("Fetched salary:", salary)
        mongo_id = ObjectId(id)
        db_company = f"applicants_company_{company}"
        local_company = f"company_{company}"
        add_user = mongo1.db[db_company].find_one({"_id": mongo_id})
        if add_user:
            title = add_user['Job Title']
            add_user.pop("_id", None)
            add_user.pop("email",None)
            mongo2.db[local_company].delete_one({"Job Title": title, "vacancy": "YES"})
            add_user["vacancy"] = "NO"
            add_user["Salary"] = int(salary)
            if add_user["Gender"] == 'male':
                add_user["Gender"] = 1
            else:
                add_user["Gender"] = 0
            add_user["Education Level"] = reverse_ed[add_user["Education Level"]]
            print(add_user)
            mongo2.db[local_company].insert_one(add_user)
            db_company = f"applicants_company_{company}"
            mongo1.db[db_company].delete_one({"_id": ObjectId(id)})
        return redirect(url_for("add_remove"))
    else:
        return redirect(url_for("add_remove"))

@app.route("/remove-application", methods = ["POST","GET"])
def remove_application():
    if request.method == "POST":
        id = request.form.get('user_id')
        company = session.get('company')
        db_company = f"applicants_company_{company}"
        mongo1.db[db_company].delete_one({"_id": ObjectId(id)})
        return redirect(url_for("add_remove"))
    else:
        return redirect(url_for("add_remove"))

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

def remove_display():
    company = session.get('company')
    company_name = f"company_{company}"
    users_collection = mongo2.db[company_name]

    # Fetching all documents from the 'users' collection
    users = users_collection.find({"vacancy" : "NO"})

    # Convert MongoDB documents to a list of dictionaries and serialize the _id
    user_list = []
    for user in users:
        user_data = {
            "id": str(user['_id']),  # Convert ObjectId to string
            "age": user.get('Age', ''),
            "gender": user.get('Gender', ''),
            "yearsOfExperience": user.get('Years of Experience', ''),
            "jobRole": user.get('Job Role', ''),
            "jobTitle": user.get('Job Title', ''),
            "salary" : user.get('Salary', '')
        }
        user_list.append(user_data)
    return render_template("ar_employee.html", users=user_list)

@app.route("/remove", methods = ["POST", "GET"])
def remove():
    company = session.get('company')
    name = f"company_{company}"
    if request.method == "POST":
        id = request.form.get("user_id")
        collection = mongo2.db[name]
        collection.update_one({"_id": ObjectId(id)}, {"$set": {"vacancy": "YES"}})
        return remove_display()
    else:
        return remove_display()

@app.route("/vacancy", methods=["GET"])
def vacancy():
    em = session.get('email')  # Get the user's email from the session
    vacant_list = []  # Initialize an empty list to hold the vacant positions

    # Retrieve all user profiles associated with the email
    user_profiles = mongo1.db.applicants.find({"email": em})
    user_job_roles = [profile.get("Job Title") for profile in user_profiles]  # Collect job roles

    # Loop through each company to check for vacancies
    for company_num in range(1, 6):  # Iterate from 1 to 5
        company_name = f"company_{company_num}"  # Construct company name
        vacant_positions = mongo2.db[company_name].find({"vacancy": "YES"})  # Fetch vacant positions
        print(vacant_positions)
        # Check each vacant position against the user's job roles
        for v in vacant_positions:
            if v.get('Job Title') in user_job_roles:
                user = {
                    "company": company_num,
                    "position": v.get('Job Title')
                }  # Check for job title match
                vacant_list.append(user)  # Add the vacant position to the list

    return render_template("vacancy.html", vacancies=vacant_list)
    # Render the vacancy page with the list of vacant positions

@app.route("/add_application", methods = ["POST","GET"])
def add_company():
    if request.method == "POST":
        app_company = request.form.get('company')
        app_company = f"applicants_company_{app_company}"
        jobtitle = request.form.get('position')
        email = session.get('email')
        application_profile = mongo1.db.applicants.find_one({"email": email, "Job Title": jobtitle})
        if application_profile:
            application_profile.pop('_id', None)
            mongo1.db[app_company].insert_one(application_profile)
        else:
            return redirect(url_for("vacancy"))

        return redirect(url_for("vacancy"))
    else:
        return redirect(url_for("vacancy"))

if __name__ == "__main__":
    app.run(debug=True)
