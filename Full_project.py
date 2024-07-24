from flask import Flask, request, render_template, redirect, url_for, session
import subprocess
from pymongo import MongoClient
from flask_mail import Mail, Message
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from new_person import capture_images



client=MongoClient('mongodb+srv://Pasupathikumar:MSpk.819@facedetection.g4nbyn9.mongodb.net/')
database=client['SIgnup']
collection=database['login_details']
feedback_data=database['Feedback']

app = Flask(__name__, template_folder='Template', static_folder='Static')
app.secret_key='|\|extBr@i|\|'

gmail_user = "kumarmarimuthu99@gmail.com"  # Your Gmail email address
gmail_password = 'lbndxwnaxfcjpzzb'  # Your Gmail app-specific password
receiver_email='pasupathi.k@nextbraintech.com'

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/feedback', methods=['POST'])
def feedback():
    name=request.form.get('name')
    mail_id=request.form.get('email')
    feedbacks=request.form.get('message')
    contents={
        'Name': name,
        "Mail_id": mail_id,
        "Feedback": feedbacks

    }
    feedback_received=f"Feedback content from user\n Name: {name} \n Mail_id: {mail_id} \n Feedback: {feedbacks}"

    feedback_data.insert_one(contents)
    msg = MIMEMultipart()
    msg["From"] = mail_id
    msg["To"] = receiver_email
    msg["Subject"] = "Jarvis AI"
    message = feedback_received
    msg.attach(MIMEText(message, "plain"))
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(gmail_user, gmail_password)

    server.sendmail(mail_id, receiver_email, msg.as_string())

    return redirect(url_for("main"))



@app.route('/login.html', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        Mail_id=request.form['Mail_id']
        Password = request.form['Password']
        user=collection.find_one({'Mail_id': Mail_id, 'Password': Password})
        print(user)
        if user:
            session['Mail_id'] = user['Mail_id']
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials.."

    return render_template('login.html')

@app.route('/Sign up.html', methods = ['POST', 'GET'])
def sign():
    return render_template('Sign up.html')

@app.route('/submit', methods=['POST'])
def form_submit():
    First_Name = request.form.get('First Name')
    Last_Name = request.form.get('Last Name')
    User_Name = request.form.get('User Name')
    Gender = request.form.get('gender')
    DOB = request.form.get('dob')
    Mail_id = request.form.get('Mail_id')
    Password = request.form.get('password')
    content = {
            'First Name': First_Name,
            'Last Name': Last_Name,
            'User Name': User_Name,
            'Gender': Gender,
            'DOB': DOB,
            'Mail_id': Mail_id,
            'Password': Password

        }
    Added_details = collection.find_one({'Mail_id': Mail_id})

    if Added_details:
        return render_template('login.html')
    else:
        collection.insert_one(content)

    return render_template('login.html')





@app.route('/go to login.html')
def go_back():
    return render_template('go to login.html')


@app.route('/model_detection.html')
def index():

    return render_template('model_detection.html')

@app.route('/run-python-code')
def run_python_code():
    try:
        subprocess.run(["python3", "face_final_detection.py"], universal_newlines=True)
        result = "Attendance added successfully"
        return result
    except Exception as e:
        return str(e)

@app.route('/Add_new_person', methods=['GET', 'POST'])
def add_new_person():
    if request.method == 'POST':
        input_value=request.form['new_person']
        num_images_to_capture=5

        capture_images(input_value, num_images_to_capture)


    return redirect(url_for('run_python_code'))


if __name__ == '__main__':
    app.run(debug=True)
