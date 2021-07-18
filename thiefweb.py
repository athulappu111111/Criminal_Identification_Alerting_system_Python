from flask import Flask, render_template, Response , request,copy_current_request_context
from flask.helpers import flash
import cv2
import face_recognition
import threading
import numpy as np
import os
from datetime import datetime
import pyautogui as pag
import csv
#import win64api


app=Flask(__name__)
camera = cv2.VideoCapture(0)

abhijith = face_recognition.load_image_file("Training_images/abhijith.jpg")
abhijith_encoding = face_recognition.face_encodings(abhijith)[0]

athul = face_recognition.load_image_file("Training_images/athul.jpg")
athul_encoding = face_recognition.face_encodings(athul)[0]

irfhad = face_recognition.load_image_file("Training_images/irfhad.jpg")
irfhad_encoding = face_recognition.face_encodings(irfhad)[0]

sreerag = face_recognition.load_image_file("Training_images/sreerag.jpg")
sreerag_encoding = face_recognition.face_encodings(sreerag)[0]

swathi = face_recognition.load_image_file("Training_images/swathi.jpg")
swathi_encoding = face_recognition.face_encodings(swathi)[0]

thief = face_recognition.load_image_file("Training_images/thief.jpg")
thief_encoding = face_recognition.face_encodings(thief)[0]

known_face_encodings = [
    abhijith_encoding,
    irfhad_encoding,
    sreerag_encoding,
    swathi_encoding,
    thief_encoding,
    athul_encoding
]
known_face_names = [
    "abhijith",
    "irfhad",
    "sreerag",
    "swathi",
    "thief",
    "athul"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def detectThief(name):
    with open('thief.csv', 'r+',encoding='UTF8', newline='') as f:
        myDataList = f.readlines()
        for line in myDataList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            writer = csv.writer(f)

        # write the header
            writer.writerow((name,dtString))



def gen_frames():  
    while True:
        ret, frame = camera.read()  
        if not ret:
            break
        else:
            
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "UNKNOWN"
                
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
                if name=="UNKNOWN":
                    pag.alert(text="Unknown user", title="Alert")
                    continue
                else:
                    continue

            

            
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

               
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                detectThief(name)
                print(name)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')
database={'user':'123'}

@app.route('/form_login',methods=['POST','GET'])
def login():
    name1=request.form['username']
    pwd=request.form['password']
    if name1 not in database:
        return render_template('index.html',info='Invalid User')
    else:
        if database[name1]!=pwd:
            return render_template('index.html',info='Invalid Password')
        else:
            #flash("Unknown USer")
            return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__=='__main__':
    app.run(debug=True)