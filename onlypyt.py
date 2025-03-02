import os
import cv2
import tkinter as tk
import easyocr
from sys import exit

# Tworzenie folderów, jeśli nie istnieją
os.makedirs("change", exist_ok=True)
os.makedirs("output", exist_ok=True)

drawing = False
start_point = None
selected_roi = None
image, image_copy = None, None
image_path = None
def choose_file():
    """Otwiera okno dialogowe do wyboru pliku."""
    root = tk.Tk()
    root.withdraw()
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(title="Wybierz plik obrazu dla onlypyt", filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    root.destroy()
    return file_path if file_path else None

def draw(event, x, y, flags, param):
    """Funkcja obsługi rysowania prostokąta."""
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
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        if (x2 - x1) >= 28 and (y2 - y1) >= 28:
            selected_roi = (y1, y2, x1, x2)

def ai(im, x1, y1):
    """Wykrywanie tekstu za pomocą EasyOCR."""
    global image, image_path
    current_dir = os.path.dirname(__file__)
    model_dir = os.path.join(current_dir, 'model')
    reader = easyocr.Reader(["pl"], gpu=False, download_enabled=False, model_storage_directory=model_dir)

    image_copy = image.copy()
    resized = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    results = reader.readtext(gray_image)
    li = []
    
    for (bbox, text, _) in results:
        if any(char.isdigit() for char in text):  # Filtrujemy tylko liczby
            (top_left, _, bottom_right, _) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            top_left = (int(top_left[0] / 2) + x1, int(top_left[1] / 2) + y1)
            bottom_right = (int(bottom_right[0] / 2) + x1, int(bottom_right[1] / 2) + y1)

            # Sprawdzamy, czy współrzędne są poprawne
            if (0 <= top_left[0] < image.shape[1] and 0 <= top_left[1] < image.shape[0] and
                0 <= bottom_right[0] < image.shape[1] and 0 <= bottom_right[1] < image.shape[0]):
                
                cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
                cropped_part = image_copy[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

                if cropped_part.size != 0:
                    li.append((top_left, bottom_right, cropped_part))
    if li:
        import edit
        edit.main(lister=li, im=image, i=image_path)

def main():
    """Główna funkcja programu."""
    global image, image_copy, selected_roi, image_path    
    
    image_path = choose_file()
    if not image_path:  # Jeśli użytkownik nie wybierze pliku -> wyjdź z programu
        cv2.destroyAllWindows()
        exit()

    image = cv2.imread(image_path)  # Wczytanie obrazu
    if image is None:
        cv2.destroyAllWindows()
        exit()
    image_copy = image.copy()
    cv2.namedWindow("Edytor Obrazu")
    cv2.setMouseCallback("Edytor Obrazu", draw)

    while True:
        cv2.imshow("Edytor Obrazu", image_copy)
        key = cv2.waitKey(1) & 0xFF
        if cv2.getWindowProperty("Edytor Obrazu", cv2.WND_PROP_VISIBLE) < 1:
            cv2.destroyAllWindows()
            exit()
        if key == ord("q") or key == ord("Q"):
            cv2.destroyAllWindows()
            exit()
        elif key in (ord("c"), ord("C")) and selected_roi:
            y1, y2, x1, x2 = selected_roi
            cropped_image = image[y1:y2, x1:x2]

            if cropped_image.size != 0:
                ai(cropped_image, x1, y1)
                break
        elif key in (ord("v"), ord("V")):
            ai(image_copy, 0, 0)
            break

    cv2.destroyAllWindows()



main()





#pyinstaller --icon=icon.ico --add-data "C:/Users/mateu/Desktop/OCR/model;model" --onefile --windowed --noconsole onlypyt.py