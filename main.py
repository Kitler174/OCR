from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # zmień tę ścieżkę na swoją, jeśli potrzebne


def ocr_image(image_path):
    # Otwórz obraz
    img = Image.open(image_path)
    
    # Użyj Tesseract do rozpoznania tekstu
    text = pytesseract.image_to_string(img)
    
    return text

if __name__ == '__main__':
    # Ścieżka do obrazu
    image_path = 'obraz.png'  # zmień na właściwą ścieżkę do pliku

    # Wykonaj OCR i wyświetl tekst
    extracted_text = ocr_image(image_path)
    print("Rozpoznany tekst:", extracted_text)