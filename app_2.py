from flask import Flask, request, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os
import subprocess
import glob
import tempfile

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index_2.html')

@socketio.on('audio_stream')
def handle_audio_stream(data):
    try:
        audio_data = data['audio']  # This will be the audio data sent from the client

        # Save the audio data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio_file:
            tmp_audio_file.write(audio_data)
            tmp_audio_file_path = tmp_audio_file.name

        # Process the audio and generate the face-mesh animation
        output_video_file = process_audio(tmp_audio_file_path)

        # Send back the video file path to the client
        emit('animation_frame', {'video_path': output_video_file})

    except Exception as e:
        emit('error', {'message': str(e)})

def process_audio(audio_file):
    try:
        # The audio file is already at 16 kHz, so you can skip the conversion step
        prefix = "16khz"  # Define your desired prefix here
        original_filename = os.path.basename(audio_file.split('.')[0])
        suffix = audio_file.split(".")[-1]
        new_filename = f"{original_filename}_{prefix}.{suffix}"
        converted_audio_file = os.path.join('uploads', new_filename)

        # Save the audio file directly without conversion
        os.rename(audio_file, converted_audio_file)

        # Step 2: Run the model
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

        return output_video_file

    except Exception as e:
        raise Exception(f'An error occurred during audio processing: {str(e)}')

@app.route('/video/<filename>')
def video_file(filename):
    # Serve the generated video file
    return send_from_directory(directory='demo/output/head/iter_0110000/', path=filename)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)