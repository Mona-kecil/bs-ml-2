import pytesseract
import cv2


def preprocess_image(image):
    scaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_applied = clahe.apply(scaled)

    denoised = cv2.bilateralFilter(
        clahe_applied, d=5, sigmaColor=50, sigmaSpace=50)

    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=21,
        C=8)

    edges = cv2.Canny(denoised, 50, 150)

    combined = cv2.bitwise_or(thresh, edges)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(combined, kernel, iterations=1)

    final = cv2.medianBlur(dilated, 3)

    return final


def read(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\  --psm 6'

    text = pytesseract.image_to_string(image, config=config)

    results = [line.strip() for line in text.splitlines() if line.strip()]

    return results
