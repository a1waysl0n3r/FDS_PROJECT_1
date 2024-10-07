import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from catboost import CatBoostRegressor
import io
import os


company_1 = pd.read_csv("csv_data/company_1.csv")
company_2 = pd.read_csv("csv_data/company_2.csv")
company_3 = pd.read_csv("csv_data/company_3.csv")
company_4 = pd.read_csv("csv_data/company_4.csv")
company_5 = pd.read_csv("csv_data/company_5.csv")

print("reached1")
companies = [company_1,company_2,company_3,company_4,company_5]
cb_model = []
model_filenames = []
def standardize():
    print("Reached Standardize")
    scaler = StandardScaler()
    for company in companies:
        df = pd.DataFrame(company["Education Level"])
        company["Education Level Standardized"] = scaler.fit_transform(df)
        print(company.iloc[:, 4:])


def model_creator():
    print("Reached model creator")
    model_filenames = [f'model_company_{i + 1}.cbm' for i in range(len(companies))]
    for idx, company in enumerate(companies):
        X = company[['Age', 'Gender', 'Years of Experience', 'Job Title', 'Education Level Standardized']]
        y = company['Salary']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=40)

        model = CatBoostRegressor(
            iterations=1000,
            learning_rate=0.1,
            depth=6,
            cat_features=[3],
            verbose=200,
        )
        model.fit(x_train, y_train)
        cb_model.append(model)

        # Corrected: Save the model with the correct filename
        model.save_model(model_filenames[idx])  # Use idx directly here


def load_models():
    model_filenames = [f'model_company_{i + 1}.cbm' for i in range(len(companies))]  # Start from 1 for consistency
    cb_models = []

    for filename in model_filenames:
        if os.path.exists(filename):
            print(f"Loading model from {filename}...")
            model = CatBoostRegressor()
            model.load_model(filename)
            cb_models.append(model)
        else:
            print(f"Model file {filename} does not exist. Please train the model first.")

    return cb_models


def predictor(learn_model, x_test):
    y_predict = []
    x_test_arr = []
    count = 0
    for i in range(0,5):
        changer = companies[i]
        job_title = x_test['Job Title'].iloc[0]
        dummy = x_test.copy()
        row = changer[changer['Job Title'] == job_title]
        dummy["Education Level Standardized"] = row["Education Level Standardized"]
        x_test_arr.append(dummy)
    for model in learn_model:
        y_predict.append(model.predict(x_test_arr[count]))
        count += 1
    return y_predict

def plotter(y_predict):
    print("Reached model creator")
    data = {
        'company_1' : y_predict[0],
        'company_2' : y_predict[1],
        'company_3' : y_predict[2],
        'company_4' : y_predict[3],
        'company_5' : y_predict[4]
    }
    x_axis = list(data.keys())
    y_axis = [y.item() for y in y_predict]
    print("x_axis:", x_axis)
    print("y_axis:", y_axis)

    fig = plt.figure(figsize=(20,10))
    plt.bar(x_axis, y_axis, width = 0.2, color = 'blue')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return img

def run():
    print("Reached run")
    standardize()
    all_models = model_creator()
    return all_models