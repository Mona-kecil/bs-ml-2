import cv2
from ocr import preprocess_image, read
import os

license_plate_classifier = cv2.CascadeClassifier(
    './models/haarcascade_russian_plate_number.xml'
)

FOLDER_PATH = os.path.join(os.getcwd(), 'license_plates')


def extract_roi(image):
    """PASS ONLY GRAYSCALE IMAGE HERE"""
    license_plates = license_plate_classifier.detectMultiScale(image)

    if len(license_plates) == 0:
        print("Not detected")
        return

    for (x, y, w, h) in license_plates:
        roi = image[y:y+h, x:x+w]
        equalized = cv2.equalizeHist(roi)
        thresh = cv2.threshold(
            equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        contours = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(
                largest_contour)

            cropped_plate = roi[y_cont:y_cont +
                                int(0.8 * h_cont), x_cont:x_cont+w_cont]

            return cropped_plate


def video_feed():
    video_stream = cv2.VideoCapture(1)
    while True:
        ret, frame = video_stream.read()
        last_detected_plate = None

        if not ret:
            raise RuntimeError('Cannot read from video stream.')

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        license_plates = license_plate_classifier.detectMultiScale(gray)

        for (x, y, w, h) in license_plates:
            roi = gray[y:y+h, x:x+w]
            equalized = cv2.equalizeHist(roi)
            thresh = cv2.threshold(
                equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            contours = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(
                    largest_contour)
                upper_crop = int(h_cont * 0.8)
                cropped_plate = roi[y_cont:y_cont +
                                    upper_crop, x_cont:x_cont+w_cont]

                processed_plate = preprocess_image(cropped_plate)
                text = read(processed_plate)

                if text != last_detected_plate:
                    last_detected_plate = text
                    print(f'Detected text: {text}')
                    cv2.imwrite('./detected/license.jpg', processed_plate)
                    print("Saved to /detected/license.jpg")

                cv2.imshow('processed license plate', processed_plate)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    video_stream.release()
    cv2.destroyAllWindows()


def photo_mode():
    image_files = [file for file in os.listdir(
        FOLDER_PATH) if file.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if not image_files:
        raise RuntimeError("No images found")

    for file in image_files:
        file_path = os.path.join(FOLDER_PATH, file)
        print(f'Processing: {file}')

        image = cv2.imread(file_path)
        if image is None:
            print(f"{file} cannot be processed, skipping file...")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        try:
            processed_image = preprocess_image(gray)
            text = read(processed_image)[0]
            print(f"Detected text: {text}")

        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue


if __name__ == '__main__':
    photo_mode()
