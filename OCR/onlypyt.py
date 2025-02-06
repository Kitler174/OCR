import cv2
import easyocr
import edit
import os
import tkinter as tk
from tkinter import filedialog
#pyinstaller --onefile --add-data "/home/mateusz/Desktop/OCR/model:model" --windowed onlypyt.py
# Tworzenie folderów, jeśli nie istnieją
os.makedirs("change", exist_ok=True)
os.makedirs("output", exist_ok=True)

drawing = False
start_point = None
selected_roi = None
image, image_copy = None, None

def choose_file():
    """Otwiera okno dialogowe do wyboru pliku"""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Wybierz plik obrazu")
    return file_path

def draw(event, x, y, flags, param):
    global start_point, drawing, image_copy, selected_roi

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        image_copy = image.copy()
        cv2.rectangle(image_copy, start_point, (x, y), (0, 255, 255), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x1, y1 = start_point
        x2, y2 = x, y
        width, height = abs(x2 - x1), abs(y2 - y1)

        if width >= 28 and height >= 28:
            selected_roi = (min(y1, y2), max(y1, y2), min(x1, x2), max(x1, x2))

def main():
    global image, image_copy, selected_roi, image_path

    image_path = choose_file()
    if not image_path:
        return

    image = cv2.imread(image_path)
    if image is None:
        return

    image_copy = image.copy()
    
    cv2.namedWindow("Edytor Obrazu")
    cv2.setMouseCallback("Edytor Obrazu", draw)
    t = True
    while t:
        cv2.imshow("Edytor Obrazu", image_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("c") and selected_roi is not None:
            t = False
            y1, y2, x1, x2 = selected_roi
            cropped_image = image[y1:y2, x1:x2]

            if cropped_image.size == 0:
                continue

            ai(cropped_image, x1, y1)
        elif key == ord("v"):
            t = False
            ai(image_copy, 0, 0)

    cv2.destroyAllWindows()

def ai(im, x1, y1):
    global image, image_path
    image_copy = image.copy()
    resized = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    reader = easyocr.Reader(['pl'], download_enabled=False, model_storage_directory=os.path.join(os.path.dirname(__file__), 'model'))
    results = reader.readtext(gray_image)
    li = []
    for (bbox, text, prob) in results:
        if any(char.isdigit() for char in text):
            (top_left, _, bottom_right, _) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            top_left = (int(top_left[0] / 2) + x1, int(top_left[1] / 2) + y1)
            bottom_right = (int(bottom_right[0] / 2) + x1, int(bottom_right[1] / 2) + y1)

            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

            cropped_part = image_copy[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            if cropped_part.size == 0:
                continue

            li.append((top_left, bottom_right, cropped_part))

    edit.main(lister=li, im=image, i=image_path)

main()
