from PIL import Image
import pytesseract
import re
import cv2
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # zmień tę ścieżkę na swoją, jeśli potrzebne


def ocr_with_coordinates(image_path):
    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    return data


def get_numbers_positions(data):
    numbers_positions = []
    for i in range(len(data['text'])):
        text = data['text'][i]
        if text.strip() and re.match(r'^\d+(\.\d+)?$', re.sub(r'[^0-9.,]', '', text)):  # Sprawdzamy, czy tekst to liczba (z opcjonalną kropką)
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            numbers_positions.append((re.sub(r'[^0-9.,]', '', text), x, y, w, h))
    
    return numbers_positions

def print_numbers_positions(numbers_positions):
    for number, x, y, w, h in numbers_positions:
        print(f"Liczba: '{number}'\nPozycja: (x={x}, y={y}, w={w}, h={h})")

def draw_and_save(image_path, numbers_positions, output_path='wynik.png'):
    # Wczytanie obrazu z OpenCV
    img = cv2.imread(image_path)

    for number, x, y, w, h in numbers_positions:
        # Rysowanie czerwonej kropki (średnica 4px)
        center = (x + w // 2, y + h // 2)  # Środek prostokąta
        cv2.circle(img, center, 2, (0, 0, 255), -1)  # Czerwony punkt, promień 2 px
        
        # Rysowanie czerwonego kwadratu 4x4 px
        top_left = (x, y)
        bottom_right = (x + 4, y + 4)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), -1)  # Czerwony kwadrat
    
    # Zapisz wynikowy obraz
    cv2.imwrite(output_path, img)

if __name__ == '__main__':
    image_path = 'obraz1.png'  # zmień na właściwą ścieżkę do pliku
    ocr_data = ocr_with_coordinates(image_path)
    numbers_positions = get_numbers_positions(ocr_data)
    print_numbers_positions(numbers_positions)
    draw_and_save(image_path, numbers_positions, "wynik1.png")