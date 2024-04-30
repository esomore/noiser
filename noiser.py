import sqlite3
from flask import Flask, render_template, send_from_directory, jsonify
import os
import pyaudio
import wave
import audioop
from threading import Thread
from datetime import datetime
from flask import send_file
import time

app = Flask(__name__)

# Create a SQLite database and a table to store the recordings
conn = sqlite3.connect('recordings.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        filename TEXT
    )
''')
conn.commit()


@app.route('/')
def index():
    if not os.path.exists('recordings'):
        os.makedirs('recordings')
    files = os.listdir('recordings')
    return render_template('index.html', files=files)

@app.route('/recordings/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file(os.path.join('recordings', filename))

@app.route('/inform', methods=['POST'])
def inform():
    # Handle the POST request here
    return 'OK', 200

@app.route('/update-noises', methods=['GET'])
def update_noises():
    # Handle the GET request here
    return 'OK', 200

@app.route('/recordings', methods=['GET'])
def get_recordings():
    conn = sqlite3.connect('recordings.db')  # Create a new connection
    c = conn.cursor()
    c.execute('SELECT * FROM recordings')
    recordings = [{'id': id, 'date': date, 'time': time, 'filename': filename} for id, date, time, filename in c.fetchall()]
    conn.close()  # Close the connection when you're done with it
    return jsonify(recordings)

def record_audio():
    chunk = 2048
    sample_format = pyaudio.paInt16
    channels = 1  # Change this to 1
    fs = 22050
    threshold = 500
    record_time = 5  # Duration to record after detecting noise

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    input=True,
                    input_device_index=2,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []
    recording = False
    start_time = None

    while True:
        data = stream.read(chunk)
        rms = audioop.rms(data, 2)

        if not recording and rms > threshold:
            print('Recording started')
            recording = True
            start_time = time.time()
            frames.append(data)
            print('Noise detected')  # Print a message when a noise is detected
        elif recording:
            if time.time() - start_time < record_time:
                frames.append(data)
            else:
                print('Recording stopped')
                recording = False
                save_to_file(frames, p.get_sample_size(sample_format), channels, fs)
                frames = []
                start_time = None

    stream.stop_stream()
    stream.close()
    p.terminate()

def save_to_file(frames, sample_size, channels, rate):
    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Use the timestamp in the filename
    filename = f'recordings/noise_{timestamp}.wav'

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_size)
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Create a new SQLite connection
    conn = sqlite3.connect('recordings.db')
    c = conn.cursor()

    # Save the recording's date, time, and filename to the database
    c.execute('INSERT INTO recordings (date, time, filename) VALUES (?, ?, ?)', (date, time, filename))
    conn.commit()

    # Close the connection when you're done with it
    conn.close()

def start_recording():
    t = Thread(target=record_audio)
    t.start()

if __name__ == "__main__":
    start_recording()
    app.run(host='0.0.0.0', port=8080)
