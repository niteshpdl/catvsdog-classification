from flask import Flask, render_template, request, jsonify, flash
import os
import requests
import base64
from PIL import Image
import uuid
import atexit
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
uploaded_files = {}
cleanup_lock = threading.Lock()

def cleanup_old_files():
    current_time = time.time()
    with cleanup_lock:
        files_to_remove = []
        for filepath, timestamp in uploaded_files.items():
            if current_time - timestamp > 1800:
                files_to_remove.append(filepath)
        
        for filepath in files_to_remove:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                del uploaded_files[filepath]
                print(f"Cleaned up old file: {filepath}")
            except Exception as e:
                print(f"Error cleaning up {filepath}: {e}")

def cleanup_all_uploads():
    with cleanup_lock:
        for filepath in list(uploaded_files.keys()):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Cleaned up file on shutdown: {filepath}")
            except Exception as e:
                print(f"Error cleaning up {filepath} on shutdown: {e}")

atexit.register(cleanup_all_uploads)

def background_cleanup():
    while True:
        time.sleep(300)
        cleanup_old_files()

cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(path):
    try:
        # Simple rule-based prediction for demo
        # You can replace this with actual model logic later
        
        img = Image.open(path).convert('RGB')
        
        # Simple heuristic based on image characteristics
        # This is just for demo - replace with your actual model
        width, height = img.size
        
        # Analyze dominant colors (very basic approach)
        img_small = img.resize((50, 50))
        pixels = list(img_small.getdata())
        
        # Simple color analysis
        brown_orange_count = 0
        gray_count = 0
        
        for pixel in pixels:
            r, g, b = pixel
            # Simple color detection
            if r > g and r > b and r > 100:  # Reddish/orange (dog-like)
                brown_orange_count += 1
            elif abs(r - g) < 30 and abs(g - b) < 30:  # Grayish
                gray_count += 1
        
        # Simple prediction logic
        if brown_orange_count > gray_count:
            confidence = min(0.65 + (brown_orange_count / len(pixels)), 0.95)
            return f"Dog (Confidence: {confidence:.2%})"
        else:
            confidence = min(0.60 + (gray_count / len(pixels)), 0.92)
            return f"Cat (Confidence: {confidence:.2%})"
            
    except Exception as e:
        print(f"Error in prediction: {e}")
        return "Unable to analyze image. Please try another image."

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    image_path = None

    if request.method == "POST":
        if 'image' not in request.files:
            flash('No file selected')
            return render_template("index.html", prediction=prediction, image_path=image_path)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No file selected')
            return render_template("index.html", prediction=prediction, image_path=image_path)
        
        if file and allowed_file(file.filename):
            cleanup_old_files()
            
            filename = str(uuid.uuid4()) + "." + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            file.save(filepath)
            
            with cleanup_lock:
                uploaded_files[filepath] = time.time()
            
            prediction = predict_image(filepath)
            image_path = f"uploads/{filename}"
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or BMP files.')

    return render_template("index.html", prediction=prediction, image_path=image_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
