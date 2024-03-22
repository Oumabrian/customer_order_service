from flask import Flask, request, jsonify, send_file
import os
import cv2
import numpy as np
import sqlite3
import random
import string



app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploaded_videos'
app.config['OUTPUT_FOLDER'] = 'processed_videos'
app.config['DATABASE'] = 'motorists.db'

# Ensure the upload, output, and database folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Function to connect to the database
def get_database_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    return conn

# Function to create the motorists table in the database
def create_motorists_table():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS motorists
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       plate_number TEXT,
                       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Create the motorists table if it doesn't exist
create_motorists_table()

# Define retrieve_data endpoint
@app.route('/retrieve_data', methods=['GET'])
def retrieve_data():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM motorists')
    data = cursor.fetchall()
    conn.close()
    return jsonify({'data': data})

# Define view_database endpoint
@app.route('/view_database', methods=['GET'])
def view_database():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM motorists')
    data = cursor.fetchall()
    conn.close()
    return jsonify({'data': data})

# Define upload_video endpoint
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part'})

    video = request.files['video']

    if video.filename == '':
        return jsonify({'error': 'No selected video file'})

    # Save the uploaded video to a specific directory
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(video_path)

    # Process the uploaded video for plate recognition
    processed_video_link = process_video(video_path, video.filename)

    return jsonify({'message': 'Video uploaded successfully', 'processed_video_link': processed_video_link})

# Function to process uploaded video for plate recognition
def process_video(video_path, filename):
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Change codec to MP4V
        processed_video_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        out = cv2.VideoWriter(processed_video_path, fourcc, fps, (width, height))

        # Process each frame of the video
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Perform plate recognition on each frame
            plate_number = recognize_plate(frame)

            # Save plate number to database
            save_plate_number(plate_number)

            # Write the processed frame to the output video
            out.write(frame)

        # Release resources
        cap.release()
        out.release()

        return f"/processed_videos/{filename}"

    except Exception as e:
        print(f"Error processing video: {e}")

# Function to recognize license plate in a frame
def recognize_plate(frame):
    # Implement license plate recognition (not implemented in this example)
    # Placeholder implementation: return a random plate number
    return 'ABC123'

# Function to save plate number to database
def save_plate_number(plate_number):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO motorists (plate_number) VALUES (?)', (plate_number,))
    conn.commit()
    conn.close()
    
def recognize_plate(frame):
    # Placeholder implementation: generate a random plate number
    plate_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return plate_number
# HTML form to upload video
upload_form = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Upload</title>
</head>
<body>
    <h1>Upload Video</h1>
    <form action="/upload_video" method="POST" enctype="multipart/form-data">
        <input type="file" name="video" accept="video/*">
        <button type="submit">Upload</button>
    </form>
</body>
</html>
'''

# Define index endpoint to serve HTML form
@app.route('/')
def index():
    return upload_form

# Define endpoint to play processed video
@app.route('/play_processed_video/<filename>')
def play_processed_video(filename):
    processed_video_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(processed_video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
