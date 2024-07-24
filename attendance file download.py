from pymongo import MongoClient
import csv
import os

client=MongoClient('mongodb+srv://Pasupathikumar:MSpk.819@facedetection.g4nbyn9.mongodb.net/')
database=client['Jarvis']
login_collection=database['Master Attendance']

file_dir='Files'
os.makedirs(file_dir, exist_ok=True)

login_file=f'{file_dir}/Login.csv'

attendance_file=f'{file_dir}/master_attendance.csv'

login_data=login_collection.find()

with open(login_file, 'w', newline='') as login_csv_datas:
    csv_writer=csv.DictWriter(login_csv_datas, fieldnames=login_data[0].keys())
    csv_writer.writeheader()
    for document in login_data:
        csv_writer.writerow(document)

print('Done')


