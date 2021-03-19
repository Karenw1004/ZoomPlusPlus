import cv2
import dlib
import numpy as np

def ShapeToNp(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def MaskToEye(mask, side):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask

def addpupil(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        moment = cv2.moments(cnt)
        pr = int(moment['m10']/moment['m00'])
        pl = int(moment['m01']/moment['m00'])
        if right:
            pr += mid
        cv2.circle(img, (pr, pl), 4, (0, 0, 255), 2)
    except:
        pass

def islooking(thresh):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        moment = cv2.moments(cnt)
        return True
    except:
        return False

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("https://github.com/r883l717/581ET/raw/master/shape_68.dat")
#predictor = dlib.shape_predictor('shape_68.dat')

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

cap = cv2.VideoCapture('t1.mp4')
ret, img = cap.read()
thresh = img.copy()    

#cv2.namedWindow('image')
kernel = np.ones((9, 9), np.uint8)

def nothing(x):
    pass

while(True):
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = ShapeToNp(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = MaskToEye(mask, left)
        mask = MaskToEye(mask, right)
        mask = cv2.dilate(mask, kernel, 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(eyes_gray, 50, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)
        thresh = cv2.medianBlur(thresh, 3)
        thresh = cv2.bitwise_not(thresh)
        print("R:{},L:{},SUM:{}".format(islooking(thresh[:, 0:mid]), islooking(thresh[:, mid:]), islooking(thresh[:, 0:mid]) or islooking(thresh[:, mid:])))
'''
        addpupil(thresh[:, 0:mid], mid, img)
        addpupil(thresh[:, mid:], mid, img, True)
        for (x, y) in shape[36:48]:
             cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
    cv2.imshow('eyes', img)
    cv2.imshow("image", thresh)
'''
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
