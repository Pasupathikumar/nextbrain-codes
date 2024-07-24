import face_recognition
import cv2
import os
import numpy as np
from deepface import DeepFace
from datetime import datetime, timedelta
import yagmail
from keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from mtcnn import MTCNN
from pymongo import MongoClient

global count_content, croped, person_counts

mail_count=0

client=MongoClient('mongodb+srv://Pasupathikumar:MSpk.819@facedetection.g4nbyn9.mongodb.net/')
database=client['SIgnup']

collection=database['Attendance list']
login_collection=database['login_details']


jarvis_database=client['Jarvis']

attendance_count = jarvis_database[datetime.now().strftime("%Y-%m-%d")]

model=load_model('Models/gender_detection.model')

detector=MTCNN()

current_date=datetime.now()
date=current_date.date()

unknown_directory=f'Unknown/{date}'
os.makedirs(unknown_directory, exist_ok=True)

sender_mail='kumarmarimuthu99@gmail.com'
app_password='lbndxwnaxfcjpzzb'
receiver='pasupathi.k@nextbraintech.com'
cc_mail='arunkumar.p@nextbraintech.com'
subject='Face detection project for Attendance system'

directory_path='data-new'

gender_label=['Male', 'Female']

cascade=cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def findEncodings():
    encodeList = []
    classNames = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".JPG") or file.endswith(".png"):
                curImgPath = os.path.join(root, file)
                curImg = cv2.imread(curImgPath)
                curImg = cv2.resize(curImg, (225, 225))
                curImg = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(curImg)
                if len(face_locations) > 0:
                    encoded_face = face_recognition.face_encodings(curImg, face_locations)[0]
                    encodeList.append(encoded_face)
                    name = os.path.basename(root)
                    classNames.append(name)
    return encodeList, classNames

encoded_face_train, classNames = findEncodings()

def mail_content(gender, date, time, image):
    yag=yagmail.SMTP(sender_mail, app_password)
    yag.send(receiver, subject, contents=['Unknown person is detected by Camera', f'Gender: {gender}', f'Date: {date}', f'Time: {time}'], attachments=[image])


    print('Mail Send Successfully')

def gender_age_detection(frame):
    result=DeepFace.analyze(frame, actions=['gender', 'age', 'emotion'], detector_backend='opencv')

    for detection in result:
        gender_result=detection['gender']
        gender_final_result=max(gender_result, key=gender_result.get)

        age=detection['age']

        emotion_result=detection['emotion']
        emotion=max(emotion_result, key=emotion_result.get)

        return gender_final_result, age, emotion
def own_model_gender_detection(frame):
    face = cv2.resize(frame, (96, 96))
    normalization = face.astype('float') / 255.0
    image = img_to_array(normalization)
    gender = np.expand_dims(image, axis=0)
    gender_predict = model.predict(gender)[0]

    idx = np.argmax(gender_predict)

    return idx
count=1
def image_path(frame):
    global count

    img=f'Unknown person {count}.JPG'
    img_path=os.path.join(unknown_directory, img)
    cv2.imwrite(img_path, frame)
    count+=1
    print(count)

    return img_path

def attendance(name, gender):
    global mail_id, mail_count
    now = datetime.now()
    time = now.strftime('%I:%M:%S:%p')
    date = now.strftime('%d-%B-%Y')

    content={
        "Name": name,
        "Gender": gender,
        "Date": date,
        "Time": time,
        "Attendance":"Present"
    }

    attendance_list=collection.find_one({"Name": name, "Date": date})

    if attendance_list:
        print('Attendance added')
    else:
        collection.insert_one(content)
        print("Attendance added successfully")

        result=login_collection.find({"First Name":name})
        for i in result:
            mail_count+=1
            mail_id=i.get("Mail_id")

            yag_mail=yagmail.SMTP(sender_mail, app_password)

            yag_mail.send(mail_id, subject=f'{date} Attendance Details', contents=['<h3>Your Attendance added Successfully</h3>', f"Sender Mail ID: {sender_mail}",
                                                                                        f'Name: {name}', f'Gender: {gender}', f'Date: {date}', f'Time: {time}'])
            if mail_count == 1:
                print("Mail sended")
            else:
                print(f'{mail_count} Mail sended')


# Capture video from webcam
#cap = cv2.VideoCapture(0)
#cap=cv2.VideoCapture('rtsp://admin:srivas123@192.168.1.21')
#cap=cv2.VideoCapture('/home/pasupathikumar/Downloads/Gender2.mp4')
cap=cv2.VideoCapture('/home/pasupathikumar/Downloads/pasupathikumar.webm')

personname={}
known_person_count=0

person_counts={name: 0 for name in classNames}


while True:
    success, img = cap.read()
    faces=detector.detect_faces(img)



    for face in faces:
        x, y, w, h = face['box']
        croped=img[x:x+w, y:y+h]
        #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        faces_in_frame = face_recognition.face_locations(imgS)
        encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)
        unknown_detected = False

        for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
            matches = face_recognition.compare_faces(encoded_face_train, encode_face)
            faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
            matchIndex = np.argmin(faceDist)

            if not matches[matchIndex]:
                unknown_detected = True
                break


        if unknown_detected:

            now = datetime.now()
            date=now.date()
            time=now.time()

            image=image_path(croped)

            gender_detection = own_model_gender_detection(img)
            gender = gender_label[gender_detection]

            mail_content(gender, date, time, image)

        tolerance = 0.5

        for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
            matches = face_recognition.compare_faces(encoded_face_train, encode_face, tolerance=tolerance)
            faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
            matchIndex = np.argmin(faceDist)

            if matches[matchIndex]:
                name = classNames[matchIndex]
                y1, x2, y2, x1 = faceloc

                gender_detection = own_model_gender_detection(img)
                gender = gender_label[gender_detection]

                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, name, (x1, y1 - 45), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, gender, (x1, y1 - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                attendance(name, gender)

            else:
                name = 'Unknown'
                y1, x2, y2, x1 = faceloc
                # since we scaled down by 4 times
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                #cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
                cv2.putText(img, name, (x1, y1 - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                #print('Unknown person detected')
            print(name, gender)

            if len(personname)==0 or (name not in personname):
                #print("klhdfvkghlbdhk : ",personname.keys())
                personname[name]={"Attendance":datetime.now(),"detectcount":1,"nextchecktime":datetime.now()+timedelta(seconds=30)}
                cv2.putText(img, name+" Attendance added", (x1, y1 - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
            elif datetime.now()>personname.get(name).get("nextchecktime"):
                personname[name].update({"detectcount":personname.get(name).get("detectcount")+1,"nextchecktime":datetime.now()+timedelta(seconds=30)})
                cv2.putText(img, name+"detect again", (x1, y1 - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

#{"_id":name}


    cv2.imshow('webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(personname)


cap.release()
cv2.destroyAllWindows()
