import sys

def process_audio(file_path):
    # Placeholder for audio processing logic
    print(f"Processing audio file: {file_path}")
    # Add your processing code here

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_audio.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    process_audio(audio_file)