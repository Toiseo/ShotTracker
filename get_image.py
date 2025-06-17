import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

s, shot_img = cam.read()

assert s is not None

#cv2.imshow("bild", shot_img)
#cv2.waitKey(0)
cv2.imwrite('shot.jpg', shot_img)