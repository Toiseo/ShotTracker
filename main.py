from flask import Flask, render_template, jsonify, send_file, request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask_socketio import SocketIO, send, emit
from dataclasses import dataclass
import numpy as np
import point_counter

import threading
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2


CAM_INTERVAL_SECONDS = 1
CAM_WIDTH = 1280
CAM_HEIGHT = 720
CORRECTED_SIZE = (640, 640)


app = Flask(__name__, static_url_path='/static', static_folder='static')
socketio = SocketIO(app, async_mode='gevent')

@dataclass
class State:
    cam = None
    ref_img = None
    target_img = None
    last_target_img = None
    should_recapture_ref_img = False
    contours = None
    def __init__(self):
        self.contours = point_counter.compute_contours()

@dataclass
class arucoMarker:
    id: int
    corners: np.ndarray
    center: tuple

state = State()
state_lock = threading.RLock()

def encode_im(im):
    return cv2.imencode('.png', im)[1].tobytes()

def console_log(message):
    socketio.emit('consoleLog', {'message': message})

def console_error(message):
    socketio.emit('consoleError', {'message': message})


def detect_and_assign_aruco_markers(detector, img):
    corners, ids, _ = detector.detectMarkers(img)
    markers = []
    if ids is not None:
        for i, id in enumerate(ids):
            corners_ = corners[i]
            center = (int(np.mean(corners_[:, 0])), int(np.mean(corners_[:, 1])))
            markers.append(arucoMarker(id=id[0], corners=corners_, center=center))
    for marker in markers:
        cornerIdx = 0
        if marker.id == 0:
            cornerIdx = 2
        elif marker.id == 1:
            cornerIdx = 3
        elif marker.id == 2:
            cornerIdx = 0   
        elif marker.id == 3:
            cornerIdx = 1
        pos = marker.corners[0][cornerIdx]
        pos = (int(pos[0]), int(pos[1]))
        marker.center = pos
    return markers
        

def get_marker_by_id(arucoMarkers, id):
    for marker in arucoMarkers:
        if marker.id == id:
            return marker
    return None

def correct_perspective(img, arucoMarkers):
    if not arucoMarkers:
        raise ValueError("No ArUco markers found in the image.")
    topLeftMarker = get_marker_by_id(arucoMarkers, 0)
    topRightMarker = get_marker_by_id(arucoMarkers, 1)
    bottomRightMarker = get_marker_by_id(arucoMarkers, 2)
    bottomLeftMarker = get_marker_by_id(arucoMarkers, 3)
    if None in [topLeftMarker, topRightMarker, bottomRightMarker, bottomLeftMarker]:
        raise ValueError("Could not find all four corner markers.")

    pts1 = np.float32([
        topLeftMarker.center,
        topRightMarker.center,
        bottomRightMarker.center,
        bottomLeftMarker.center
    ])
    pts2 = np.float32([
        [0, 0],
        [CORRECTED_SIZE[0], 0],
        [CORRECTED_SIZE[0], CORRECTED_SIZE[1]],
        [0, CORRECTED_SIZE[1]]
    ])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(img, matrix, CORRECTED_SIZE)
    return result   

def detect_bullet_holes(thresh, targetIn=None):
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    antal = 1  
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:antal]
    if targetIn is None:
        target = cv2.imread("static/Target.png")
    else:
        target = targetIn.copy()
    for cnt in sorted_contours:
        area = cv2.contourArea(cnt)
        #cv2.drawContours(ref_img, [cnt], -1, (0, 255, 0), 2)
        if area > 10:
            x, y, w, h = cv2.boundingRect(cnt)
            center = (x + w//2, y + h//2)
            target = cv2.circle(target, center, 10, (0, 0, 0), -1)
            x,y = center
            score = get_shot_score(x, y, state.contours)
            socketio.emit('shotDetected', score)
    return target

def get_shot_score(x, y, contours):
    score = point_counter.test_point(x, y, contours)
    if score is None:
        return 0
    return 10-score 

def check_camera(detector):
    with state_lock:
        ret, im = state.cam.read()
        if ret:
            arucoMarkers = detect_and_assign_aruco_markers(detector, im)
            completeAruco = len(arucoMarkers) == 4
            if not completeAruco:
                console_error('aruco error')            
            else:
                im = correct_perspective(im, arucoMarkers)
            if state.ref_img is None or state.should_recapture_ref_img:
                if state.ref_img is not None and completeAruco:
                    if state.ref_img.shape[:2] == im.shape[:2]:
                        tempRefImg = state.ref_img.copy()
                        tempIm = im.copy()
                        _, _, tempRefImg = cv2.split(tempRefImg)
                        _, _, tempIm = cv2.split(tempIm)
                        diff = cv2.absdiff(tempRefImg, tempIm)
                        diff = cv2.threshold(diff, 60, 255, cv2.THRESH_BINARY)[1]
                        if state.target_img is None:
                            state.last_target_img = cv2.imread("static/Target.png")
                            state.target_img = detect_bullet_holes(diff)
                        else:
                            state.last_target_img = state.target_img.copy()
                            state.target_img = detect_bullet_holes(diff, state.target_img)
                        socketio.emit('scoreImage', encode_im(state.target_img))
                        socketio.emit('diffImage', encode_im(diff))
                    else:
                        state.ref_img = im.copy()
                console_log('Recaptured reference image')
                state.ref_img = im
                state.should_recapture_ref_img = False
                socketio.emit('refImage', encode_im(im))
                return
        else:
            console_error('Failed to capture image from camera')

def camera_task():
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cam.set(cv2.CAP_PROP_FOCUS, 0)
    cam.set(cv2.CAP_PROP_CONTRAST , 25)
    cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    
    with state_lock:
        state.cam = cam

    # Setup aruco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 23
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    parameters.perspectiveRemoveIgnoredMarginPerCell = 0.05
    parameters.minMarkerPerimeterRate = 0.03
    parameters.maxMarkerPerimeterRate = 4.0 
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)   

    try:
        while True:
            try:
                check_camera(detector)
            except Exception as e:
                console_error(f'Error in camera processing: {str(e)}')
            socketio.sleep(0.1)
    finally:
        cam.release()


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('requestRefImage')
def handle_request_ref_image():
    with state_lock:
        socketio.emit('refImage', encode_im(state.ref_img) if state.ref_img is not None else None)

@socketio.on('setFocus')
def handle_set_focus(focus):
    with state_lock:
        focus_value = float(focus)
        state.cam.set(cv2.CAP_PROP_FOCUS, focus_value)

@socketio.on('recaptureRefImage')
def handle_message():
    with state_lock:
        state.should_recapture_ref_img = True
        console_log('Set should recapture reference image to True')

@socketio.on('updateCameraSettings')
def handle_update_camera_settings(data):
    with state_lock:
        if 'focus' in data:
            if int(data['autoFocus']) == 0:
                state.cam.set(cv2.CAP_PROP_FOCUS, float(data['focus']))
        if 'autoFocus' in data:
            state.cam.set(cv2.CAP_PROP_AUTOFOCUS, int(data['autoFocus']))
        if 'autoExposure' in data:
            state.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, int(data['autoExposure']))
            if int(data['autoExposure']) == 0 and 'exposure' in data:
                state.cam.set(cv2.CAP_PROP_EXPOSURE, float(data['exposure']))
        console_log('Camera settings updated')
    

@socketio.on('acceptShot')
def handle_accept_shot():
    with state_lock:
        pass

@socketio.on('restartServer')
def handle_restart_server():
    with state_lock:
        state.ref_img = None
        state.target_img = None
        state.last_target_img = None
        state.should_recapture_ref_img = False
        console_log('Server restarted and all images cleared')
        socketio.emit('serverRestarted')   
            
@socketio.on('rejectShot')
def handle_reject_shot():
    with state_lock:
        if state.last_target_img is not None:
            state.target_img = state.last_target_img.copy()
            socketio.emit('scoreImage', encode_im(state.target_img))


if __name__ == '__main__':
    socketio.start_background_task(camera_task)
    socketio.run(app, debug=True, host='0.0.0.0', port=1337)
    contours = point_counter.compute_contours()
