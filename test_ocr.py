import easyocr
import cv2

img = cv2.imread('./license_2.jpeg')
blur = cv2.GaussianBlur(img, (3, 3), 0)
gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)[1]

cv2.imshow('a', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

reader = easyocr.Reader(['en', 'id'])
result = reader.readtext(thresh, detail=0)
print(result)
