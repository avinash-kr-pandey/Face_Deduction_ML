import cv2
import dlib
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Load the pre-trained model
predictor_path = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
glasses_image_path = "glasses.png"
glasses = cv2.imread(glasses_image_path, cv2.IMREAD_UNCHANGED)

def add_glasses(image, landmarks, glasses):
    left_eye = landmarks[36]
    right_eye = landmarks[45]
    glasses_width = right_eye[0] - left_eye[0]
    glasses_height = int(glasses.shape[0] * glasses_width / glasses.shape[1])
    resized_glasses = cv2.resize(glasses, (glasses_width, glasses_height))
    top_left = (left_eye[0], left_eye[1] - glasses_height // 2)
    roi = image[top_left[1]:top_left[1] + glasses_height, top_left[0]:top_left[0] + glasses_width]
    alpha_glasses = resized_glasses[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_glasses
    for c in range(0, 3):
        roi[:, :, c] = (alpha_glasses * resized_glasses[:, :, c] +
                        alpha_background * roi[:, :, c])
    image[top_left[1]:top_left[1] + glasses_height, top_left[0]:top_left[0] + glasses_width] = roi

@app.route('/process-image', methods=['POST'])
def process_image():
    file = request.files['image']
    filename = secure_filename(file.filename)
    file.save(filename)
    image = cv2.imread(filename)
    faces = detector(image, 1)
    for face in faces:
        shape = predictor(image, face)
        landmarks = [(p.x, p.y) for p in shape.parts()]
        add_glasses(image, landmarks, glasses)
    result_image_path = "result_" + filename
    cv2.imwrite(result_image_path, image)
    return jsonify({"result_image": result_image_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
