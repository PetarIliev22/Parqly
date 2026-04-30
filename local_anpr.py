import re, time, cv2, queue, requests, numpy as np
import easyocr
from collections import defaultdict
from queue import Queue
from threading import Thread
from ultralytics import YOLO

from server import format_plate
from server import get_resource_path, update_plate, run_flask

Thread(target=run_flask, daemon=True).start()
 
CAMERA_SOURCE = 0
PLATE_TIMEOUT = 1  
CONFIRM_FRAMES = 2
FRAME_SKIP = 3      
QUEUE_MAX = 1    
LATEST_FRAME = None
LATEST_TIME = 0

BG_PLATE_REGEX = re.compile(r'^[A-Z]{1,2}[0-9]{4}[A-Z]{2}$')

frame_queue = Queue(maxsize=QUEUE_MAX)
seen_counts = defaultdict(int)
confirmed = set()

reader = easyocr.Reader(['bg', 'en'], gpu=False)
model = YOLO(get_resource_path("iliev_licence_plate.pt"))
model.fuse() 

# тук се приемат кадри от камерата
def capture_frames():
    global LATEST_FRAME, LATEST_TIME
    
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        return "Camera not found"
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
        LATEST_FRAME = frame
        LATEST_TIME = time.time()
    

# тук се извършва обработката - премахва дублирани и невалидни символи 
def clean_text(text):
    text = text.upper()
    text = re.sub(r'^(.)\1+', r'\1', text)     
    text = re.sub(r'[^A-Z0-9]', '', text)     
    return text
 
# OCR за разпознаване на номера от изображение
def ocr_plate(img):
    res = reader.readtext(
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        detail=1
    )
    if not res:
        return None
    # взимаме резултатите с confidence > 0.6
    filtered = [r for r in res if r[2] > 0.6]

    if not filtered:
        return None

    # съединяваме по реда на координатите (ляво -> дясно)
    filtered = sorted(filtered, key=lambda x: x[0][0][0])

    text = ''.join([r[1] for r in filtered])
    text = clean_text(text)

    if 6 <= len(text) <= 9:
        return text
    return None

# тук се проверява дали номера е валиден и отговаря на BG_REGEX
# def is_valid_plate(text):
#     if not text:
#         return False
#     if not any(c.isalpha() for c in text):
#         return False
#     if not any(c.isdigit() for c in text):
#         return False
#     if len(text) < 5:
#         return False
#     return True

def is_valid_plate(text): 
    return bool(BG_PLATE_REGEX.match(text))

# Функция за запис на потвърден номер в Supabase
Thread(target=capture_frames, daemon=True).start()
print("Parking System Started. Press 'q' to QUIT.")

COOLDOWN = 10
CONFIRM_FRAMES = 2

last_seen_time = {}
seen_counts = {}
last_yolo = 0

while True:
    frame = LATEST_FRAME
    now = time.time()

    if frame is None:
        continue

    if now - last_yolo < 0.4:
        cv2.imshow("ParQly | ANPR Systems", frame)
        cv2.waitKey(1)
        continue

    last_yolo = now

    results = model.predict(frame, conf=0.5, iou=0.5, verbose=False)
    boxes = results[0].boxes.xyxy

    if boxes is None or len(boxes) == 0:
        cv2.imshow("ParQly | ANPR Systems", frame)
        cv2.waitKey(1)
        continue

    box = max(boxes, key=lambda b: (b[2]-b[0]) * (b[3]-b[1]))
    x1, y1, x2, y2 = map(int, box)

    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    plate_roi = frame[y1:y2, x1:x2]

    text = ocr_plate(plate_roi)

    if not text:
        cv2.imshow("ParQly | ANPR Systems", frame)
        cv2.waitKey(1)
        continue

    valid = is_valid_plate(text)

    color = (0, 255, 0) if valid else (0, 0, 255)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    if valid:
        for k in list(seen_counts.keys()):
            if k != text:
                seen_counts[k] = 0

        seen_counts[text] = seen_counts.get(text, 0) + 1

        if seen_counts[text] >= CONFIRM_FRAMES:

            if text not in last_seen_time or now - last_seen_time[text] > COOLDOWN:

                last_seen_time[text] = now
                seen_counts[text] = 0

                try:
                    requests.post(
                        "http://127.0.0.1:5000/api/plate",
                        json={"plate": text},
                        timeout=2
                    )
                except:
                    pass

                update_plate(format_plate(text), True)

    cv2.imshow("ParQly | ANPR Systems", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    time.sleep(0.01)

cv2.destroyAllWindows()