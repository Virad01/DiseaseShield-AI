from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = "tarp_project"

heartDiseaseModel = pickle.load(open('TenYearCHDPrediction.pkl', 'rb'))
lungCanerModel = pickle.load(open('lungcancer.pkl', 'rb'))
diabetesModel = pickle.load(open('diabetes.pkl', 'rb'))

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tarp'

mysql = MySQL(app)


@app.route('/')
def signup():
    return render_template('signup.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
        return render_template('signin.html')


@app.route('/home', methods=['POST'])
def home():
    if request.method == 'POST':
        userDetails = request.form
        cur = mysql.connection.cursor()
        if (len(userDetails) == 2):
            email = str(userDetails['email'])
            password = str(userDetails['password'])
            session['email'] = email
            query = "Select * from user where email = %s"
            cur.execute(query, (email,))
            data = cur.fetchone()
            if (data is not None and data[2] == password):
                cur.close()
                return render_template('home.html')
            else:
                return render_template('login.html', data='Invalid Credentials/Email not registered. Try again!')
        elif (len(userDetails) == 3):
            email = str(userDetails['email'])
            password = str(userDetails['password'])
            confirmPassword = str(userDetails['confirmPassword'])
            session['email'] = email
            query = "Select * from user where email = %s"
            cur.execute(query, (email,))
            data = cur.fetchone()
            if data is not None:
                cur.close()
                return render_template('signup.html', data='This email is registered already. Please try another '
                                                             'email or log in!')
            else:
                if password == confirmPassword:
                    query2 = "Insert Into user(email, password) Values(%s,%s)"
                    cur.execute(query2, (email, password))
                    cur.close()
                    return render_template('home.html')
                else:
                    return render_template('signup.html', data="Passwords don't match. Please try again")


@app.route('/homeredirect')
def homeredirect():
    return render_template('home.html')


@app.route('/coronary-heart-disease-prediction-form')
def heartDiseasePredictionForm():
    return render_template('coronary-heart-disease-prediction.html')


@app.route('/lung-cancer-prediction-form')
def lungCancerPredictionForm():
    return render_template('lung-cancer-prediction.html')


@app.route('/diabetes-prediction-form')
def diabetesPredictionForm():
    return render_template('diabetes-prediction.html')


@app.route('/heartDiseasePrediction', methods=['POST'])
def heartDiseasePrediction():
    if 'email' in session:
        userEmail = session['email']
        features = [[int(request.form['gender']), int(request.form['age']), int(request.form['education']),
                     int(request.form['currentSmoker']), int(request.form['cigsPerDay']), int(request.form['BPMeds']),
                     int(request.form['prevalentStroke']), int(request.form['prevalentHyp']),
                     int(request.form['diabetic']),
                     float(request.form['totChol']), float(request.form['sysBP']), float(request.form['diaBP']),
                     float(request.form['BMI']), float(request.form['heartRate']), float(request.form['glucose'])]]
        features = np.array(features)
        output = heartDiseaseModel.predict_proba(features)
        truthProb = output[0][1]
        query = "INSERT INTO HeartDiseasePrediction(userEmail, probability,savedTime) VALUES(%s,%s,now())"
        cur = mysql.connection.cursor()
        cur.execute(query, (userEmail, truthProb))
        if truthProb > 0.6:
            return render_template('coronary-heart-disease-prediction.html',
                                   data='You have a risk of developing coronary heart disease. Probability '
                                        'of developing heart disease is {0:.2f}'.format(truthProb))
        else:
            return render_template('coronary-heart-disease-prediction.html', data='You are healthy. Probability '
                                                                                  'of developing heart disease is {0:.2f}'.format(
                truthProb))
    else:
        return render_template("signin.html", data="Please login first!")


@app.route('/lungCancerPrediction', methods=['POST'])
def lunCancerPrediction():
    if 'email' in session:
        userEmail = session['email']
        int_features = [int(request.form['gender']), int(request.form['age']), int(request.form['smoking']),
                        int(request.form['yellowFingers']), int(request.form['anxiety']),
                        int(request.form['peerPressure']), int(request.form['chronicDisease']),
                        int(request.form['fatigue']), int(request.form['allergy']), int(request.form['wheezing']),
                        int(request.form['alcohol']), int(request.form['coughing']),
                        int(request.form['shortnessOfBreath']), int(request.form['swallowingDifficulty']),
                        int(request.form['chestPain'])]
        features = [np.array(int_features)]
        output = lungCanerModel.predict_proba(features)
        truthProb = output[0][1]
        query = "INSERT INTO lungcancerprediction(userEmail, probability,savedTime) VALUES(%s,%s,now())"
        cur = mysql.connection.cursor()
        cur.execute(query, (userEmail, truthProb))
        if truthProb > 0.6:
            return render_template('lung-cancer-prediction.html',
                                   data='You have a risk of developing lung cancer. Probability '
                                        'of developing lung cancer is {0:.2f}'.format(truthProb))
        else:
            return render_template('lung-cancer-prediction.html', data='You are healthy. Probability '
                                                                       'of developing lung cancer is {0:.2f}'.format(
                truthProb))
    else:
        return render_template("signin.html", data="Please login first!")


@app.route('/diabetesPrediction', methods=['POST'])
def diabetesPrediction():
    if 'email' in session:
        userEmail = session['email']
        int_features = [int(request.form['pregnancies']), int(request.form['glucose']), int(request.form['bloodPressure']), int(request.form['skinThickness']), int(request.form['insulin']), int(request.form['bmi']), int(request.form['pedigreefn']), int(request.form['age'])]
        features = [np.array(int_features)]
        output = diabetesModel.predict_proba(features)
        truthProb = output[0][1]
        query = "INSERT INTO diabetesprediction(userEmail, probability,savedTime) VALUES(%s,%s,now())"
        cur = mysql.connection.cursor()
        cur.execute(query, (userEmail, truthProb))
        if truthProb > 0.6:
            return render_template('diabetes-prediction.html',
                                   data='You have a risk of developing diabetes. Probability '
                                        'of developing diabetes is {0:.2f}'.format(truthProb))
        else:
            return render_template('diabetes-prediction.html', data='You are healthy. Probability '
                                                                    'of developing diabetes is {0:.2f}'.format(
                truthProb))
    else:
        return render_template("signin.html", data="Please login first!")


if __name__ == "__main__":
    app.run(debug=True)
