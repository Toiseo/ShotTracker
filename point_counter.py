import cv2
import numpy as np

def resize_contour_to_area(contour, target_area):
    current_area = cv2.contourArea(contour)
    if current_area == 0:
        raise ValueError("Contour area is zero — cannot scale.")

    scale_factor = np.sqrt(target_area / current_area)

    M = cv2.moments(contour)
    if M['m00'] == 0:
        raise ValueError("Contour has zero moments — cannot find center.")
    cx = M['m10'] / M['m00']
    cy = M['m01'] / M['m00']
    center = np.array([cx, cy])

    scaled = (contour.reshape(-1, 2) - center) * scale_factor + center
    return scaled.astype(np.int32).reshape(-1, 1, 2)

def compute_contours():
    img = cv2.imread('static/Target.png')

    blank = np.zeros_like(img)

    gray = cv2.split(img)[2]
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    currentContour = None
    centeredContours = []
    for i, c in enumerate(contours):    
        first = i%2==0
        if first:
            currentContour = c
        else:
            oldArea = cv2.contourArea(currentContour)
            currentArea = cv2.contourArea(c)
            newArea = (oldArea + currentArea) / 2
            newC = resize_contour_to_area(currentContour, newArea)
            centeredContours.append(newC)
            currentContour = None
    return centeredContours
            
def test_point(x, y, contours):
    for i, contour in enumerate(contours):
        if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
            return i