import os, re, time, cv2, queue
import easyocr
from dotenv import load_dotenv
from collections import defaultdict
from queue import Queue
from supabase import create_client
from server import update_plate, run_flask
from threading import Thread
from ultralytics import YOLO

Thread(target=run_flask, daemon=True).start()

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CAMERA_SOURCE = 0
TABLE_NAME = "plates" 
PLATE_TIMEOUT = 1  
CONFIRM_FRAMES = 2  
FRAME_SKIP = 2      
QUEUE_MAX = 1       

BG_PLATE_REGEX = re.compile(r'^[A-Z]{1,2}[0-9]{4}[A-Z]{2}$')

frame_queue = Queue(maxsize=QUEUE_MAX)
seen_counts = defaultdict(int)
confirmed = set()

reader = easyocr.Reader(['bg', 'en'], gpu=False)
model = YOLO("iliev_licence_plate.pt")
model.fuse() 

# тук се приемат кадри от камерата
def capture_frames():
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        return "Camera not found"
    while True:
        ret, frame = cap.read() # ret = дали кадъра (frame) е валиден True/False
        if ret and not frame_queue.full():
            frame_queue.put(frame)
            continue
        time.sleep(0.05)

# тук се извършва обработката - премахва дублирани и невалидни символи 
def clean_text(text):
    text = text.upper()
    text = re.sub(r'^(.)\1+', r'\1', text)     
    text = re.sub(r'[^A-Z0-9]', '', text)     
    return text
 
# OCR за разпознаване на номера от изображение
def ocr_plate(img):
    # списък с резултати
    res = reader.readtext( 
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        detail=0
    )
    if not res:
        return None
    text = clean_text(''.join(res))
    return text if 6 <= len(text) <= 9 else None  

# тук се проверява дали номера е валиден и отговаря на BG_REGEX
def is_valid_plate(text): 
    return bool(BG_PLATE_REGEX.match(text))

# Функция за запис на потвърден номер в Supabase
def save_plate_db(text):
    if not is_valid_plate(text):
        print("Invalid plate:", text)
        return
    try:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        res = supabase.table(TABLE_NAME).select("plate_text").eq("plate_text", text).execute()
        if res.data:
            supabase.table(TABLE_NAME).update({"status": "OUT", "time_out": now}).eq("plate_text", text).eq("status", "IN").execute()
            print(" --- Plate already exists:", text)
        else:
            supabase.table(TABLE_NAME).insert({"plate_text": text, "time_in": now}).execute()
    except Exception as e:
        print("Supabase error:", e)

Thread(target=capture_frames, daemon=True).start()
print("Parking System Started. Press 'q' to QUIT.")

COOLDOWN = 10
last_seen_time = {}
frame_count = 0

while True:
    try:
        frame = frame_queue.get(timeout=0.01)
    except queue.Empty:
        continue

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    now = time.time()
    results = model(frame, conf=0.4, verbose=False)
    boxes = results[0].boxes.xyxy

    if len(boxes) == 0:
        continue

    for box in boxes:
        x1, y1, x2, y2 = (int(v) for v in box)
        plate_roi = frame[y1:y2, x1:x2]

        text = ocr_plate(plate_roi)
        if not text:
            continue

        valid = is_valid_plate(text)
        color = (0,255,0) if valid else (0,0,255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, text, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        if not valid:
            continue

        seen_counts[text] += 1
        if seen_counts[text] >= CONFIRM_FRAMES:
            if text not in last_seen_time or now - last_seen_time[text] > COOLDOWN:

                last_seen_time[text] = now

                text_with_interval = f"{text[:-6]} {text[-6:-2]} {text[-2:]}"
                print("Confirmed Plate:", text_with_interval)

                save_plate_db(text)
                update_plate(text_with_interval, True)

    cv2.imshow("ParQly | ANPR Systems", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()