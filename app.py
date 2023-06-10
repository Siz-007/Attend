import cv2
import numpy as np
import pandas as pd
import face_recognition
import os
from datetime import datetime
from flask import Flask, flash, request,session, redirect, url_for,send_file, render_template, Response
from werkzeug.utils import secure_filename
import csv
import json

UPLOAD_FOLDER = r'IMAGE_FILES'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/upload',methods=['POST'])
def upload_file1():
    output=request.get_json()
    output=json.loads(output)
    session['user']=output['email']
    print(output['email'])
    if('user' in session):
        return redirect(url_for('up'))
    else:
        return render_template('index.html')

@app.route('/upload1')
def up():
    if('user' in session):
        print(session['user'])
        return render_template('upload.html')
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return render_template('index.html')





@app.route('/success', methods=['GET', 'POST'])
def success():
    if 'file' not in request.files:
        return render_template('upload.html')
    file = request.files['file']
    name=request.form['name']
    if file.filename == '':
        return render_template('upload.html')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        li=filename.split('.')
        filename=name+'.'+li[1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('upload.html')
    else:
        return render_template('upload.html')


@app.route('/index')
def index():
    """Video streaming home page."""
    f = open('attendence.csv', 'r+')
    f.truncate(0)
    f.close()
    if('user' in session):
        return render_template('index1.html')
    return render_template('index.html')


def gen():
    IMAGE_FILES = []
    filename = []
    dir_path = r'IMAGE_FILES'

    for imagess in os.listdir(dir_path):
        img_path = os.path.join(dir_path, imagess)
        img_path = face_recognition.load_image_file(img_path)  # reading image and append to list
        IMAGE_FILES.append(img_path)
        filename.append(imagess.split(".", 1)[0])

    def encoding_img(IMAGE_FILES):
        encodeList = []
        for img in IMAGE_FILES:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def takeAttendence(name):
        with open('attendence.csv', 'r+') as f:
            
            mypeople_list = f.readlines()
            nameList = []
            rollList=[]
            for line in mypeople_list:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                datestring = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{datestring}')

    encodeListknown = encoding_img(IMAGE_FILES)
    # print(len('sucesses'))

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgc = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        # converting image to RGB from BGR
        imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        fasescurrent = face_recognition.face_locations(imgc)
        encode_fasescurrent = face_recognition.face_encodings(imgc, fasescurrent)

        # faceloc- one by one it grab one face location from fasescurrent
        # than encodeFace grab encoding from encode_fasescurrent
        # we want them all in same loop so we are using zip
        for encodeFace, faceloc in zip(encode_fasescurrent, fasescurrent):
            matches_face = face_recognition.compare_faces(encodeListknown, encodeFace)
            face_distence = face_recognition.face_distance(encodeListknown, encodeFace)
            # print(face_distence)
            # finding minimum distence index that will return best match
            matchindex = np.argmin(face_distence)

            if matches_face[matchindex]:
                name = filename[matchindex].upper()
                # print(name)
                y1, x2, y2, x1 = faceloc
                # multiply locations by 4 because we above we reduced our webcam input image by 0.25
                # y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), 2, cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                takeAttendence(name)  # taking name for attendence function above

        # cv2.imshow("campare", img)
        # cv2.waitKey(0)
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        key = cv2.waitKey(20)
        if key == 27:
            break


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/attend')
def attend():
    with open('attendence.csv', 'r') as csvfile:
        csv_dict = [row for row in csv.DictReader(csvfile)]
        if len(csv_dict) == 0:
            print('csv file is empty')
            return render_template('index.html')
    data=pd.read_csv("attendence.csv",header=None)
    if data.empty:
        print("HELLO")
        return render_template("index.html")

    d1=data.values
    print(d1[0])
    print("done")
    if('user' in session):
        return render_template("attend.html",d1=d1)
    return render_template("index.html")

@app.route('/download')
def download_file():
    p="attendence.csv"
    os.system('python database.py')
    return send_file(p,as_attachment=True)


@app.route('/delete/<string:name>')
def delete(name):

    file=open('attendence.csv','r')
    red=csv.reader(file)
    l=[]
    fon=False
    for row in red:
        if len(row)==0:
            continue
        if row[0]==name:
            fon=True
        else:
            l.append(row)
    file.close()
    if fon==True:
        file=open('attendence.csv','w+',newline='')
        wrt=csv.writer(file)
        wrt.writerows(l)
        file.seek(0)
        file.close()
    with open('attendence.csv', 'r') as csvfile:
        csv_dict = [row for row in csv.DictReader(csvfile)]
        if len(csv_dict) == 0:
            print('csv file is empty')
            return render_template('index.html')
    df=pd.read_csv("attendence.csv",header=None)

    if df.empty:
        return render_template("index.html")
    d1=df.values
    
    print(df)
    if('user' in session):
        return render_template("attend.html",d1=d1)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
