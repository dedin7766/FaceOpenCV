from flask import Flask, render_template, request, jsonify
import cv2
import face_recognition
import numpy as np
import os
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_face'

# Initialize MySQL
mysql = MySQL(app)

def detect_face_encodings(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    return face_encodings, face_locations

def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    if True in matches:
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_photo')
def register_photo():
    return render_template('register_photo.html')

@app.route('/test_compare_photo')
def test_compare_photo():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, name, file_path FROM registered_faces")
    users = cursor.fetchall()
    cursor.close()
    return render_template('test_compare_photo.html', users=users)

@app.route('/register', methods=['POST'])
def register():
    if 'photo' not in request.files:
        return jsonify({'message': 'Foto tidak ditemukan'}), 400

    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({'message': 'Nama file tidak valid'}), 400

    # Simpan file ke folder uploads
    filename = secure_filename(photo.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(file_path)

    image = cv2.imread(file_path)
    name = request.form['name']
    encodings, _ = detect_face_encodings(image)
    if encodings:
        encoding = encodings[0]
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO registered_faces (name, file_path) VALUES (%s, %s)", (name, file_path))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Foto berhasil diregistrasi'}), 200
    else:
        return jsonify({'message': 'Wajah tidak terdeteksi pada foto'}), 400

@app.route('/compare', methods=['POST'])
def compare():
    user_id = request.form['user_id']
    if not user_id:
        return jsonify({'message': 'Pilih user terlebih dahulu!'}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, name, file_path FROM registered_faces WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return jsonify({'message': 'User tidak ditemukan!'}), 400

    known_image = cv2.imread(user['file_path'])
    known_encodings, _ = detect_face_encodings(known_image)
    if not known_encodings:
        return jsonify({'message': 'Wajah tidak terdeteksi pada foto user'}), 400

    if 'photo' not in request.files:
        return jsonify({'message': 'Foto tidak ditemukan'}), 400

    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({'message': 'Nama file tidak valid'}), 400

    # Simpan file ke folder uploads
    filename = secure_filename(photo.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(file_path)

    image = cv2.imread(file_path)
    face_encodings, _ = detect_face_encodings(image)

    if face_encodings:
        is_recognized = compare_faces(known_encodings, face_encodings[0])
        if is_recognized:
            return jsonify({'result': 'Wajah dikenali', 'user_id': user['id'], 'user_name': user['name']}), 200
        else:
            return jsonify({'result': 'Wajah tidak cocok'}), 200
    else:
        return jsonify({'message': 'Wajah tidak terdeteksi pada foto'}), 400

if __name__ == '__main__':
    app.run(debug=True)
