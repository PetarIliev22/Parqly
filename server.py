import time, os, sys, json, webbrowser
from flask import Flask, render_template, jsonify, Response, request
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
from threading import Event, Timer 

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "plates"

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(
    __name__, 
    template_folder=get_resource_path("templates"), 
    static_folder=get_resource_path("static")
)

CORS(app)
plate_event = Event()
latest_plate = {"text": "-", "valid": False}

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

def update_plate(text, valid):
    global latest_plate
    latest_plate = {"text": text, "valid": valid}
    print(f"Updated plate: {latest_plate}")
    plate_event.set()

def format_plate(text):
    return f"{text[:-6]} {text[-6:-2]} {text[-2:]}"

@app.route("/")
def index():
    return render_template("display.html")

@app.route("/plate")
def plate():
    return jsonify(latest_plate)

<<<<<<< HEAD
@app.route("/api/plate", methods=["POST"])
def receive_plate():

    data = request.json
    plate = data.get("plate")
    formatted_plate = format_plate(plate)
    
    if not plate:
        return jsonify({"error": "No plate"}), 400

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        res = supabase.table(TABLE_NAME)\
            .select("*")\
            .eq("plate_text", plate)\
            .eq("status", "IN")\
            .execute()

        if res.data:

            carPlate = res.data[0]
            
            if carPlate['paid'] and not carPlate['can_exit']:
                supabase.table(TABLE_NAME).update({
                    "can_exit": True,
                    "time_out": now
                }).eq("plate_text", plate).execute()
                carPlate['can_exit'] = True
                
            if not carPlate['can_exit']:
                print("NOT EXITABLE:", plate)
                update_plate(formatted_plate, False)
                return jsonify({"error": "NOT EXITABLE"}), 400
            
            supabase.table(TABLE_NAME)\
                .update({
                    "status": "OUT"
                })\
                .eq("plate_text", plate)\
                .eq("status", "IN")\
                .execute()

            print("EXIT:", plate)
            update_plate(formatted_plate, True)
        
        else:
            supabase.table(TABLE_NAME).insert({
                "plate_text": plate,
                "status": "IN",
                "paid": False,
                "can_exit": False,
                "time_in": now
            }).execute()

            print("ENTER:", plate)

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)})

=======
# Server-Sent Events - изпраща към браузъра само ако има засечен номер
>>>>>>> 3927cfbe0a5924bea7c4fd80d27ec9e74369ae94
@app.route("/plate/stream")
def plate_stream():
    def event_stream():
        last_sent = {"text": None, "valid": None}
        while True:
            plate_event.wait()
            if latest_plate != last_sent:
                data = json.dumps(latest_plate)
                yield f"data: {data}\n\n"
                last_sent = latest_plate.copy()
            time.sleep(0.1) 
            plate_event.clear()
    return Response(event_stream(), mimetype="text/event-stream")

def run_flask():
    Timer(2, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)
    