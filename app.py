import math
import os

import dlib
import time
from imutils import face_utils
from flask import Flask, request, render_template

# Load our trained detector
file_name = 'left_hand_nail_detector_all.svm'
detector = dlib.simple_object_detector(file_name)
predictor = dlib.shape_predictor('left_hand_nail_predictor.dat')

start_time = time.time()


def distance(point_1, point_2):
    if len(point_1) != 2 or len(point_2) != 2:
        return -1
    width = point_1[0] - point_2[0]
    height = point_1[1] - point_2[1]

    return math.sqrt(width * width + height * height)


def detect(frame):
    # Detect with detector
    detections = detector(frame)

    st = time.time()
    print('Detected ', len(detections))
    results = []
    for idx, detection in enumerate(detections):
        shape = predictor(frame, detection)
        shape = face_utils.shape_to_np(shape)

        center_point = (round((shape[3][0] + shape[0][0]) / 2), round((shape[3][1] + shape[0][1]) / 2))
        triangle_width = shape[0][0] - center_point[0]
        triangle_height = center_point[1] - shape[0][1]
        angle = math.degrees(math.atan(triangle_width / triangle_height))
        width = distance(shape[1], shape[2])

        result = {
            'width': width,
            'center_point': center_point,
            'rotation': angle,
            'finger': ['little', 'ring', 'middle', 'index'][idx]
        }
        results.append(result)
    print('Evaluating Completed, Total Time taken: {:.6f} seconds'.format(time.time() - st))
    return {
        'data': {
            'items': results
        }
    }


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './upload/'


def error_response(error):
    return {
        'error': {
            'message': error
        }
    }


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/recognize", methods=['GET', 'POST'])
def recognize():
    if request.method == 'GET':
        return render_template('recognize.html')
    else:
        if 'image' not in request.files:
            return error_response('Please upload an image')
        image = request.files['image']
        path = os.path.join(app.config['UPLOAD_FOLDER'], str(time.time_ns()) + image.filename)
        image.save(path)
        frame = dlib.load_rgb_image(path)
        return detect(frame)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
