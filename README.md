# 🐱🐶 Cat vs Dog Classifier

A Flask web application that uses a trained CNN model to classify images as cats or dogs with confidence scores.

## Features

- 🔍 Real-time image classification with confidence percentage
- 🎨 Modern, responsive UI with gradient design
- 🗑️ Automatic image cleanup (removes old files after 30 minutes)
- 📱 Mobile-friendly design
- ⚡ Fast prediction using TensorFlow/Keras
- 🧹 Auto-delete images when user closes the browser

## Project Structure

```
DogCatClassifier/
├── app.py                 # Main Flask application
├── cat_dog_model.h5       # Trained CNN model (from Google Colab)
├── requirements.txt       # Python dependencies
├── Procfile              # For Render deployment
├── render.yaml           # Render configuration
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── uploads/          # Temporary image storage
└── README.md             # This file
```

## Local Development

1. **Clone or download this project**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make sure your trained model `cat_dog_model.h5` is in the root directory**

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and go to:** `http://localhost:5000`

## Model Information

The model is a CNN trained on cat vs dog images with the following architecture:
- Input: 256x256x3 RGB images
- Conv2D layers with BatchNormalization and MaxPooling
- Dense layers with Dropout for regularization
- Output: Single sigmoid unit for binary classification
- Prediction > 0.5 = Dog, < 0.5 = Cat

## Deployment on Render

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Cat vs Dog Classifier"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to [Render.com](https://render.com) and sign up/login**

2. **Click "New +" and select "Web Service"**

3. **Connect your GitHub repository**

4. **Configure the deployment:**
   - **Name:** `cat-dog-classifier` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Choose Free tier for testing

5. **Advanced Settings:**
   - Set environment variable: `PYTHON_VERSION` = `3.11.0`

6. **Click "Create Web Service"**

7. **Wait for deployment** (usually takes 5-10 minutes)

### Step 3: Access Your Deployed App

Once deployed, Render will provide you with a URL like:
`https://your-app-name.onrender.com`

## Important Notes for Deployment

### Model File Size
- Make sure your `cat_dog_model.h5` file is included in your repository
- If the file is too large (>100MB), you might need to use Git LFS:
  ```bash
  git lfs track "*.h5"
  git add .gitattributes
  git add cat_dog_model.h5
  git commit -m "Add model with LFS"
  ```

### Environment Variables
- The app automatically detects the PORT from Render
- No additional environment variables needed

### Memory and Performance
- Free tier has memory limitations (~512MB)
- TensorFlow models can be memory-intensive
- Consider upgrading to paid tier for better performance

## Features Implemented

✅ **Auto Image Cleanup:**
- Files automatically deleted after 30 minutes
- Images deleted when user closes browser
- Background cleanup thread prevents storage buildup

✅ **Enhanced UI:**
- Modern gradient design
- Responsive layout for mobile devices
- Loading animations during prediction
- File selection feedback

✅ **Error Handling:**
- Model loading validation
- File type verification
- Graceful error messages

✅ **Production Ready:**
- Gunicorn WSGI server
- Proper port configuration for Render
- Thread-safe file management

## Troubleshooting

### Common Issues:

1. **Model not loading:**
   - Ensure `cat_dog_model.h5` is in the root directory
   - Check file permissions

2. **Deployment fails:**
   - Verify all files are committed to Git
   - Check requirements.txt is complete
   - Ensure model file is not too large

3. **Out of memory on Render:**
   - Consider using a smaller model
   - Upgrade to paid tier
   - Optimize image preprocessing

4. **Images not displaying:**
   - Check static folder permissions
   - Verify upload folder creation

## Model Training Code (Reference)

Your original Google Colab code structure:
```python
# Data preparation
train_ds = keras.utils.image_dataset_from_directory(...)
validation_ds = keras.utils.image_dataset_from_directory(...)

# Model architecture
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(256,256,3)),
    BatchNormalization(),
    MaxPooling2D((2,2)),
    # ... more layers
    Dense(1, activation='sigmoid')
])

# Training
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(train_ds, epochs=10, validation_data=validation_ds)

# Save model
model.save('cat_dog_model.h5')
```

## Next Steps

- [ ] Add more animal categories
- [ ] Implement user authentication
- [ ] Add prediction history
- [ ] Optimize model size for faster deployment
- [ ] Add API endpoints for mobile apps

## Support

If you encounter any issues:
1. Check the Render deployment logs
2. Verify all files are properly committed
3. Ensure your model file is accessible
4. Check memory usage in Render dashboard

---

Made with ❤️ using Flask, TensorFlow, and Render
