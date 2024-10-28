# app.py
from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
import glob

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def process_audio(audio_file):
    try:
        # Step 1: Convert audio to 16kHz using ffmpeg
        #converted_audio_file = 'uploads/converted_audio.wav'
        
        prefix = "16khz"  # Define your desired prefix here
        original_filename = os.path.basename(audio_file.split('.')[0])
        suffix = audio_file.split(".")[-1]
        new_filename = f"{original_filename}_{prefix}.{suffix}"
        converted_audio_file = os.path.join('uploads', new_filename)

        subprocess.run(['ffmpeg', '-y', '-i', audio_file, '-ar', '16000', converted_audio_file])

        # Step 2: Run the model
        # Define paths for the model inputs
        exp_name = "head"  # Example experiment name
        coef_file = "demo/input/coef/TH217.npy"  # Coefficient file path
        style_file = "demo/input/style/TH217.npy"  # Style file path
        output_video_file = f"{original_filename.split('.')[0]}.mp4"  # Output video file name

        # Construct the command to run the model
        command = [
            'python', 'demo.py',
            '--exp_name', exp_name,
            '--iter', '110000',
            '-a', converted_audio_file,
            '-c', coef_file,
            '-s', style_file,
            '-o', output_video_file,
            '-n', '1',
            '-ss', '3',
            '-sa', '1.15',
            '-dtr', '0.99',
            '--device', 'cpu'
        ]

        # Run the model command
        subprocess.run(command)

        # Run the model command
        subprocess.run(command)

        # Return the video embedded in the HTML
        return f'''
            <h2>Audio processed successfully.</h2>
            <h3>Generated Video:</h3>
            <video width="640" height="480" controls>
                <source src="/video/{output_video_file}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        ''', 200

    except Exception as e:
        return f'An error occurred during audio processing: {str(e)}', 500


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'audio' not in request.files:
            return 'No audio file part', 400
        file = request.files['audio']
        if file.filename == '':
            return 'No selected file', 400
        file.save(os.path.join('uploads', file.filename))
        #return 'File uploaded successfully', 200
        return process_audio(os.path.join('uploads', file.filename))

    except Exception as e:
        return f'An error occurred: {str(e)}', 500


@app.route('/record', methods=['POST'])
def record_audio():
    try:
        if 'audio' not in request.files:
            return 'No audio file part', 400
        file = request.files['audio']
        if file.filename == '':
            return 'No selected file', 400
        file.save(os.path.join('uploads', file.filename))
        #return 'Audio recorded successfully', 200
        return process_audio(os.path.join('uploads', file.filename))
    except Exception as e:
        return f'An error occurred: {str(e)}', 500



@app.route('/video/<filename>')
def video_file(filename):
    # Serve the generated video file
    return send_from_directory(directory='demo/output/head/iter_0110000/', path=filename)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)