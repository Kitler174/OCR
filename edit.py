import cv2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from sys import exit

# Globalne zmienne
drawing = False
start_point = None
drawn_shapes = []
image, image_copy = None, None
mouse_position = (0, 0)
def draw(event, x, y, flags, param):
    global start_point, drawing, image_copy, drawn_shapes, mouse_position, im2

    # Zapisz aktualną pozycję myszy
    mouse_position = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        # Rozpoczęcie rysowania
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        # Podgląd rysowanego kwadratu
        if drawing:
            image_copy = image.copy()
            cv2.rectangle(image_copy, start_point, (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        # Zakończenie rysowania nowego kwadratu
        if drawing:
            drawing = False
            end_point = (x, y)
            width = abs(end_point[0] - start_point[0])
            height = abs(end_point[1] - start_point[1])
            if width >= 8 and height >= 8:
                while True:
                    drawn_shapes.append((tuple(map(int, start_point)), tuple(map(int, end_point)),im2[start_point[1]:end_point[1],start_point[0]:end_point[0]]))
                    redraw_shapes()
                    return
            else:
                return

def redraw_shapes():
    """
    Funkcja do ponownego rysowania wszystkich kwadratów na obrazie.
    """
    global image_copy
    image_copy = image.copy()
    for shape in drawn_shapes:
        if isinstance(shape[1], tuple):  # Sprawdzenie poprawności formatu
            cv2.rectangle(image_copy, shape[0], shape[1], (0, 255, 0), 2)  # Rysuj kwadraty z listy

def main(lister,im,i):
    global image, image_copy, drawn_shapes, mouse_position, im2, pat
    drawn_shapes = lister
    image = im
    pat = i

    im2 = cv2.imread(i)
    if image is None:
        exit()

    image_copy = image.copy()
    for g in drawn_shapes:
        cv2.rectangle(image_copy, g[0], g[1], (0, 255, 0), 2)  # Rysuj kwadraty z listy
    # Ustaw okno i funkcję obsługi myszy
    cv2.namedWindow("Edytor Obrazu")
    cv2.setMouseCallback("Edytor Obrazu", draw)

    while True:
        # Wyświetl obraz
        cv2.imshow("Edytor Obrazu", image_copy)
        key = cv2.waitKey(1) & 0xFF
        if cv2.getWindowProperty("Edytor Obrazu", cv2.WND_PROP_VISIBLE) < 1:
            cv2.destroyAllWindows()
            exit()
        # Oczekiwanie na klawisz
        if key == ord("q") or key == ord("Q"):
            # Wyjście z programu
            cv2.destroyAllWindows()
            exit()
        elif key == ord("s") or key == ord("S"):
            finish()
            # Zapisz obraz
        elif key == ord("g") or key == ord("G"):
            # Sprawdź, czy kliknięto w któryś z kwadratów po naciśnięciu 'g'
            for i, shape in enumerate(drawn_shapes):
                if isinstance(shape[1], tuple):  # Sprawdzenie poprawności formatu
                    x1, y1 = shape[0]
                    x2, y2 = shape[1]
                    # Sprawdzanie czy kliknięto w kwadrat
                    if x1 <= mouse_position[0] <= x2 and y1 <= mouse_position[1] <= y2:
                        drawn_shapes.pop(i)  # Usuń kwadrat z listy
                        redraw_shapes()
        

def finish():
    global drawn_shapes, pat
    """
    Rysuje wypełniony prostokąt z wyśrodkowanym tekstem.
    
    :param image: Obraz, na którym rysujemy.
    :param top_left: Górny lewy róg prostokąta (x1, y1).
    :param bottom_right: Dolny prawy róg prostokąta (x2, y2).
    :param text: Tekst do umieszczenia w środku prostokąta.
    """
    # Kolor prostokąta (np. niebieski, lekko przezroczysty)
    act = 0
    pat = os.path.splitext(os.path.basename(pat))[0]
    os.makedirs("output/"+pat, exist_ok=True)

    # Tworzymy obiekt PDF
    pdf_filename = f"output/{pat}/output_{pat}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setTitle("Legenda dokumentu - "+pat)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    for g in drawn_shapes:
        act += 1
        cv2.rectangle(image, g[0], g[1], (0, 0, 255), -1)  # -1 wypełnia prostokąt
        x1, y1 = g[0]
        x2, y2 = g[1]
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        text_size = cv2.getTextSize(str(act), font, font_scale, font_thickness)[0]
        text_x = center_x - text_size[0] // 2
        text_y = center_y + text_size[1] // 2
        cv2.putText(image, str(act), (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)
        cropped_image = g[2]
        cv2.imwrite(f"change/temp_image_{act}.png", cropped_image)

    _, height = letter  # Rozmiar strony (A4 w punktach)
    img_height, img_width, _ = image.shape

    y = height - 10
    # Zapisz obraz z wypełnionymi prostokątami
    cv2.imwrite(f"output/{pat}/edited_image.png", image)
    act = 0
    for g in drawn_shapes:
        act += 1
        
        # Pobierz przycięty obraz
        image_path = f"change/temp_image_{act}.png"
        img_height, img_width, _ = g[2].shape
        if y - img_height < 50:  # Utrzymujemy odstęp na nowej stronie
            c.showPage()
            y = height - 50  # Resetuj pozycję Y

        # Dodaj obraz do PDF
        c.drawImage(image_path, 100, y - img_height-10, width=img_width, height=img_height)

        # Dodaj numer obok obrazu
        c.setFont("Helvetica", 10)
        c.drawString(100, y, f"Numer: {act}")

        # Przesuń w dół na kolejny element
        y -= img_height + 50  # 40 to odstęp między obrazkami
    c.save()
    cv2.destroyAllWindows()
    exit()
