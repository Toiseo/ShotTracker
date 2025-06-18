import cv2
import numpy as np

def ellipse_in_bounds(ellipse, img_shape):
    center, axes, angle = ellipse[0], ellipse[1], ellipse[2]
    center = tuple(map(int, center))
    axes = tuple([int(a / 2) for a in axes])
    pts = cv2.ellipse2Poly(center, axes, int(angle), 0, 360, 5)
    h, w = img_shape[:2]
    return np.all((pts[:, 0] >= 0) & (pts[:, 0] < w) & (pts[:, 1] >= 0) & (pts[:, 1] < h))

def preprocess_image(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    gray = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8), thresh)
    return thresh

def find_ellipses(contours, img):
    ellipses = []
    for contour in contours:
        if len(contour) >= 5:
            ellipse = cv2.fitEllipse(contour)
            ellipses.append((ellipse, contour))
    ellipses = sorted(ellipses, key=lambda e: max(e[0][1]), reverse=True)
    return ellipses

def test(drawn_ellipses, img, contours):
    

    contours = sorted(contours, key=cv2.contourArea, reverse=False)
    center = find_ellipse_center(drawn_ellipses, img)
    cv2.circle(img, (320, 320), 5, (0, 0, 255), -1)
    cv2.imshow('Smallest Contour', img)

def find_ellipse_center(ellipses, img=None):
    """
    Finds the rightmost pixel of the first ellipse and the leftmost pixel of the second ellipse,
    then returns the pixel in the middle between them.
    """
    if len(ellipses) < 2:
        return None
    #draw ellipse in blue
    cv2.ellipse(img, ellipses[0][0], (255, 0, 0), 1)
    # Get ellipse parameters
    ellipse1, _ = ellipses[0]
    ellipse2, _ = ellipses[1]

    # Generate ellipse points
    center1 = tuple(map(int, ellipse1[0]))
    axes1 = tuple([int(a / 2) for a in ellipse1[1]])
    angle1 = int(ellipse1[2])
    pts1 = cv2.ellipse2Poly(center1, axes1, angle1, 0, 360, 1)

    center2 = tuple(map(int, ellipse2[0]))
    axes2 = tuple([int(a / 2) for a in ellipse2[1]])
    angle2 = int(ellipse2[2])
    pts2 = cv2.ellipse2Poly(center2, axes2, angle2, 0, 360, 1)

    # Rightmost pixel of first ellipse
    rightmost1 = pts1[np.argmax(pts1[:, 0])]
    cv2.circle(img, tuple(rightmost1), 5, (0, 255, 0), -1)

    # Leftmost pixel of second ellipse
    leftmost2 = pts2[np.argmin(pts2[:, 0])]
    cv2.circle(img, tuple(leftmost2), 5, (255, 0, 0), -1)

    # Middle pixel between them
    middle = ((rightmost1[0] + leftmost2[0]) // 2, (rightmost1[1] + leftmost2[1]) // 2)
    return middle
    

def draw_main_ellipse(img, ellipses, n=2):
    drawn_ellipses = []
    for ellipse, contour in ellipses[:n]:
        if ellipse_in_bounds(ellipse, img.shape):
            cv2.ellipse(img, ellipse, (255, 255, 255), 1)
            drawn_ellipses.append(ellipse)
    return drawn_ellipses


def compute_remaining_ellipses(ellipses, img, num_ellipses=10, pixel_step=30):
    if not ellipses:
        return
    main_ellipse = ellipses[0]
    new_ellipses = []
    for i in range(1, num_ellipses):
        new_ellipse = resize_ellipse(main_ellipse, i * pixel_step)
        if ellipse_in_bounds(new_ellipse, img.shape):
            if i == num_ellipses - 1:
                center, axes, angle = new_ellipse
                min_axis = min(axes)
                circle_axes = (min_axis, min_axis)
                circle_ellipse = (center, circle_axes, angle)
                cv2.ellipse(img, circle_ellipse, (255, 0, 0), 1)
            else:
                cv2.ellipse(img, new_ellipse, (0, 255, 0), 1)
            new_ellipses.append(new_ellipse)

def resize_ellipse(ellipse, pixel_diff):
    center, axes, angle = ellipse
    new_axes = (max(axes[0] - pixel_diff, 1), max(axes[1] - pixel_diff, 1))
    return (center, new_axes, angle)

def draw_contours(img):
    thresh = preprocess_image(img)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    ellipses = find_ellipses(contours, img)
    ellipses = draw_main_ellipse(img, ellipses, n=2)
    return img

def main():
    thresh = preprocess_image('static/ref.jpg')
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.imread('static/Ref.jpg')
    ellipses = find_ellipses(contours, img)
    ellipses = draw_main_ellipse(img, ellipses, n=2)
    compute_remaining_ellipses(ellipses, img, num_ellipses=10, pixel_step=55)
    cv2.imshow('Contours', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()