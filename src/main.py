import os
import requests
import datetime

import cv2

from ocr import preprocess_image, read

PRICE_PER_HOUR: int = 2500
GRACE_PERIOD_MINUTES: int = 15
FOLDER_PATH = os.path.join(os.getcwd(), 'license_plates')

images = [f for f in os.listdir(
    FOLDER_PATH) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def menu():
    print()
    for index, file in enumerate(images, start=1):
        print(f'{index}> {file}')
    choice = input('Pilih kendaraan: ')
    try:
        clear_screen()
        choice = int(choice)
        if choice >= 1 and choice <= len(images):
            act_as(choice - 1)
        else:
            print('Out of index')
    except Exception:
        return


def get_identity(index: int) -> dict():
    """
    Returns the license plate from OCR
    """
    file_path = os.path.join(FOLDER_PATH, images[index])
    print(f'Processing {images[index]}...')

    image = cv2.imread(file_path)
    if image is None:
        print(f'Failed to process {images[index]}... Skipping file')
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    try:
        processed_image = preprocess_image(gray)
        text = read(processed_image)[0]
        return {
            'status': 'success',
            'identity': text
        }
    except Exception as e:
        print(f'Error processing {images[index]}: {str(e)}')


def act_as(index: int):
    license_plate = get_identity(index)['identity']

    payment_time: datetime.datetime

    parking_duration_minutes: int = 0
    while True:
        print()
        print(f'Current: {license_plate}')
        print(f'Parking duration (minutes): {parking_duration_minutes}')

        print('1. Enter the parking area')
        print('2. Stay for 15 minutes')
        print('3. Stay for 1 hour')
        print('4. Pay')
        print('5. Exit parking area')

        choice = input("Choose your action\n> ")
        clear_screen()
        try:
            choice = int(choice)
            if choice == 1:
                enter_area(license_plate)
            elif choice == 2:
                print('Stayed for 15 minutes...')
                parking_duration_minutes += 15
            elif choice == 3:
                print('Stayed for 60 minutes...')
                parking_duration_minutes += 60
            elif choice == 4:
                payment_time = pay(license_plate, parking_duration_minutes)
            elif choice == 5:
                if exit_area(license_plate, payment_time):
                    break
        except Exception as e:
            print(f'Exception occured: {str(e)}')
            continue


def enter_area(license_plate: str):
    url = 'http://localhost:8000/api/v1/sessions'
    entry_time = datetime.datetime.now()

    payload = {
        'license_plate': license_plate,
        'entry_time': entry_time.isoformat()
    }

    try:
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            print(f'Welcome {license_plate}')
            print('Opening gate...')
        else:
            print(f'Response: {response.status_code}\n{response.text}')

    except Exception as e:
        print(f'Error communicating with backend service: {str(e)}')


def pay(license_plate: str, parking_duration_minutes: int):
    hrs = parking_duration_minutes // 60
    mins = parking_duration_minutes % 60

    if mins >= 30:
        hrs += 1

    fee = hrs * PRICE_PER_HOUR
    print(f'Stayed for {hrs} hour(s) and {mins} minute(s)')
    print(f'Fee / hour = {PRICE_PER_HOUR}')
    print(f'Fee: {fee:,} IDR')

    while True:
        confirm_payment = input("Pay? (Y/n)")
        if confirm_payment.lower() in ['yes', 'y']:
            print(f"Paid {fee:,} IDR")
            print(f'Please leeave within {GRACE_PERIOD_MINUTES} minutes')
            break
        else:
            print("Bayar dulu bang")

    payment_time = datetime.datetime.now()
    url = 'http://localhost:8000/api/v1/payments'
    payload = {
        'license_plate': license_plate,
        'payment_method': 'mobile',
        'amount': fee,
        'payment_time': payment_time.isoformat()
    }

    try:
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            print(f'Response: {response.json()}')
            return payment_time
        else:
            print(f'Response: {response.status_code}\n{response.text}')

    except Exception as e:
        print(f'Error communicating with backend service: {str(e)}')


def exit_area(license_plate: str, payment_time: datetime.datetime):
    if payment_time is None:
        print("Please make a payment first")
        return

    grace_period_deadline = payment_time + \
        datetime.timedelta(minutes=GRACE_PERIOD_MINUTES)
    now = datetime.datetime.now()

    if now > grace_period_deadline:
        print("You are charged 1 more hour for staying too long after payment. Please pay it first")
        return False

    url = f'http://localhost:8000/api/v1/sessions/{license_plate}'
    payload = {
        'exit_time': now.isoformat()
    }

    try:
        response = requests.patch(url, json=payload, timeout=3)
        if response.status_code == 200:
            print(f'Response: {response.json()}')
            return True
        else:
            print(f'Response: {response.status_code}\n{response.text}')
    except Exception as e:
        print(f'Error communicating with backend service: {str(e)}')


if __name__ == '__main__':
    while True:
        menu()
