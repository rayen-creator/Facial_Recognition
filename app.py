from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import base64
import re
import face_recognition
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "./temp/"
FACES_FOLDER = "./faces/"
# Connect to database
client = MongoClient('mongodb://localhost:27017/')
db = client['farm_sanctuaryDB']
if db != '':
    print("* Database connected! **"+str(db))


@app.route("/", methods=['GET'])
def index():
    print("API works!")
    return "API works!"


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return 'Image saved successfully'


@app.route("/process_face", methods=['POST'])
def process_face():
    data_json = request.get_json()
    img_decoded = base64.b64decode(re.sub("data:image/jpeg;base64,", "", data_json["img_base64"]))

    img_name = str(datetime.now().strftime("%m-%d-%Y-%H-%M-%S")) + ".jpg"
    unknown_image_path = os.path.join(UPLOAD_FOLDER, img_name)
    known_image_path = os.path.join(FACES_FOLDER, data_json["login"] + ".jpg")

    with open(unknown_image_path, 'wb') as f:
        f.write(img_decoded)

    known_image = face_recognition.load_image_file(known_image_path)
    unknown_image = face_recognition.load_image_file(unknown_image_path)

    person_encoding = face_recognition.face_encodings(known_image)[0]

    try:
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results = face_recognition.compare_faces([person_encoding], unknown_encoding)
    except IndexError:
        os.remove(unknown_image_path)
        return jsonify({
            "valid": False,
            "message": "No face found",
            "login": data_json["login"]
        })

    os.remove(unknown_image_path)

    return jsonify({
        "valid": True,
        "message": "Face processed successfully",
        "login": data_json["login"]
    })


if __name__ == '__main__':
    print("--------- APP STARTED ON PORT: 5000 ---------")
    app.run(debug=True, port=5000)
