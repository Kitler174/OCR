from PIL import Image
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # zmień tę ścieżkę na swoją, jeśli potrzebne


def ocr_with_coordinates(image_path):
    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    return data


def get_numbers_positions(data):
    numbers_positions = []
    for i in range(len(data['text'])):
        text = data['text'][i]
        if text.strip() and re.match(r'^\d+(\.\d+)?$', text):  # Sprawdzamy, czy tekst to liczba (z opcjonalną kropką)
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            numbers_positions.append((text, x, y, w, h))
    
    return numbers_positions

def print_numbers_positions(numbers_positions):
    for number, x, y, w, h in numbers_positions:
        print(f"Liczba: '{number}'\nPozycja: (x={x}, y={y}, w={w}, h={h})")

if __name__ == '__main__':
    image_path = 'obraz.png'  # zmień na właściwą ścieżkę do pliku
    ocr_data = ocr_with_coordinates(image_path)
    numbers_positions = get_numbers_positions(ocr_data)
    print_numbers_positions(numbers_positions)