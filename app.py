from flask import Flask, render_template, request, jsonify, flash
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import uuid
import atexit
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # For flash messages

# Model configuration - using local file
MODEL_PATH = "cat_dog_model.h5"

# Load model with error handling
try:
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from: {MODEL_PATH}")
        model = load_model(MODEL_PATH)
        print("Model loaded successfully!")
    else:
        print(f"Error: Model file not found at {MODEL_PATH}")
        model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Track current image and cleanup
uploaded_files = {}
cleanup_lock = threading.Lock()

def cleanup_old_files():
    """Remove files older than 30 minutes"""
    current_time = time.time()
    with cleanup_lock:
        files_to_remove = []
        for filepath, timestamp in uploaded_files.items():
            if current_time - timestamp > 1800:  # 30 minutes
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
    """Clean up all uploaded files on app shutdown"""
    with cleanup_lock:
        for filepath in list(uploaded_files.keys()):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Cleaned up file on shutdown: {filepath}")
            except Exception as e:
                print(f"Error cleaning up {filepath} on shutdown: {e}")

# Register cleanup function for app shutdown
atexit.register(cleanup_all_uploads)

# Start background cleanup thread
def background_cleanup():
    while True:
        time.sleep(300)  # Check every 5 minutes
        cleanup_old_files()

cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(path):
    try:
        if model is None:
            return "Model not loaded - please check if cat_dog_model.h5 exists"
        
        img = image.load_img(path, target_size=(256, 256))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = model.predict(img_array)[0][0]
        confidence = float(prediction) if prediction > 0.5 else float(1 - prediction)
        result = "Dog" if prediction > 0.5 else "Cat"
        return f"{result} (Confidence: {confidence:.2%})"
    except Exception as e:
        print(f"Error in prediction: {e}")
        return f"Error in prediction: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    image_path = None

    if request.method == "POST":
        # Check if file was uploaded
        if 'image' not in request.files:
            flash('No file selected')
            return render_template("index.html", prediction=prediction, image_path=image_path)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No file selected')
            return render_template("index.html", prediction=prediction, image_path=image_path)
        
        if file and allowed_file(file.filename):
            # Clean up any existing files for this session
            cleanup_old_files()
            
            # Create unique filename
            filename = str(uuid.uuid4()) + "." + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            # Save the file
            file.save(filepath)
            
            # Track the file for cleanup
            with cleanup_lock:
                uploaded_files[filepath] = time.time()
            
            # Make prediction
            prediction = predict_image(filepath)
            image_path = f"uploads/{filename}"
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or BMP files.')

    return render_template("index.html", prediction=prediction, image_path=image_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
