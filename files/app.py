from flask import Flask, request, jsonify, render_template, send_file
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
from PIL import Image
from gtts import gTTS

API_KEY = ""
with open("API_KEY.txt", "r") as file:
    API_KEY = file.read()

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

def text_to_speech(text, filename="output.mp3"):
    """Convert text to speech and save it as an MP3 file."""
    tts = gTTS(text=text, lang='ne')  # 'ne' for Nepali
    filepath = os.path.join("static", filename)
    tts.save(filepath)
    return filepath

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Send image to Gemini API for description
    description = get_image_description(filepath)

    # Convert text to speech
    audio_path = text_to_speech(description)

    return jsonify({"description": description})

def get_image_description(image_path):
    """Sends the image to Gemini API and returns the description in Nepali."""
    
    # Open the image with PIL
    img = Image.open(image_path)

    # Load Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Send image with a prompt
    # response = model.generate_content([img, "Describe this image in Nepali in a few words. Do not include any english words in your response."])
    response = model.generate_content([img, "Describe this image in Nepali in beiefly. Do not include any english words in your response."])

    return response.text.strip() if response.text else "No description available."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
