from flask import Flask, request, render_template, redirect, url_for
import os
import subprocess
import soundfile as sf
import numpy as np

app = Flask(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return redirect(request.url)
    
    file = request.files['audio']
    
    if file.filename == '':
        return redirect(request.url)
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Convert audio to 16kHz
    audio_data, sample_rate = sf.read(file_path)
    if sample_rate != 16000:
        audio_data = np.interp(np.linspace(0, len(audio_data), int(len(audio_data) * 16000 / sample_rate)), 
                                np.arange(len(audio_data)), audio_data)
        sf.write(file_path, audio_data, 16000)

    # Run the processing script
    subprocess.run(['python', 'process_audio.py', file_path])

    return 'Audio processed successfully!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
