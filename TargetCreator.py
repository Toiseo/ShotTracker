# WIP SCRIPT TO DRAW A TARGET IMAGE FROM THE CAPTURED REFERENCE

import cv2
from matplotlib.pyplot import gray
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
    img = cv2.imread('static/ref.jpg', 1)
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)

    limg = cv2.merge((cl,a,b))

    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    gray = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imshow('Thresholded Image', thresh)
    cv2.waitKey(0)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    min_area = 500
    filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    return filtered_contours
            
def test_point(x, y, contours):
    for i, contour in enumerate(contours):
        if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
            return i
       
img = cv2.imread('static/Ref.jpg')
blank = np.zeros_like(img) 
computedContours = compute_contours()

for contour in computedContours:
    cv2.drawContours(blank, [contour], -1, (255, 255, 255), 2)
cv2.imshow('Contours', blank)
cv2.waitKey(0)
cv2.destroyAllWindows()