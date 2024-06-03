import cv2
import face_recognition
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk

# Fungsi untuk memilih dan memuat gambar dari file komputer
def load_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return None
    image = cv2.imread(file_path)
    return image

# Fungsi untuk mendeteksi wajah dalam gambar
def detect_face_encodings(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    return face_encodings, face_locations

# Fungsi untuk membandingkan dua gambar
def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    name = "Wajah tidak dikenali"
    color = (0, 0, 255)  # Warna merah

    if True in matches:
        name = known_name
        color = (0, 255, 0)  # Warna hijau

    return name, color

# Fungsi untuk register foto
def register_photo():
    global registered_image, known_encoding, known_name
    registered_image = load_image()
    if registered_image is not None:
        known_name = simpledialog.askstring("Input", "Masukkan nama untuk gambar terdaftar:")
        encodings, _ = detect_face_encodings(registered_image)
        if encodings:
            known_encoding = encodings[0]
            display_image(registered_image, panel, panel_label, known_name)

# Fungsi untuk tes compare foto menggunakan kamera
def test_compare_photo():
    if known_encoding is None:
        result_label.config(text="Register foto terlebih dahulu!")
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set ukuran lebar frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set ukuran tinggi frame

    while True:
        ret, frame = cap.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name, color = compare_faces([known_encoding], face_encoding)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow('Face Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Fungsi untuk menampilkan gambar di GUI
def display_image(image, panel, label, name):
    bgr_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(bgr_image)
    img_tk = ImageTk.PhotoImage(image=img)
    panel.config(image=img_tk)
    panel.image = img_tk
    label.config(text=name)

# Inisialisasi GUI
root = tk.Tk()
root.title("Face Recognition")

known_encoding = None
known_name = ""

registered_image = None

# Tombol Register Foto
register_button = tk.Button(root, text="Register Foto", command=register_photo)
register_button.pack()

# Tombol Tes Compare Foto
test_button = tk.Button(root, text="Tes Compare Foto", command=test_compare_photo)
test_button.pack()

# Label hasil perbandingan
result_label = tk.Label(root, text="")
result_label.pack()

# Panel untuk menampilkan gambar terdaftar
panel_label = tk.Label(root, text="")
panel_label.pack()
panel = tk.Label(root)
panel.pack()

root.mainloop()
