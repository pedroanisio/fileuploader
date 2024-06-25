from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

UPLOAD_FOLDER = 'uploads'
CLIPBOARD_FOLDER = 'clipboard'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'pst'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLIPBOARD_FOLDER'] = CLIPBOARD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Load SECRET_KEY from environment

# Ensure the upload and clipboard folders exist
for folder in [UPLOAD_FOLDER, CLIPBOARD_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Configure logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_properties(filename, folder):
    file_path = os.path.join(folder, filename)
    file_size = os.path.getsize(file_path)
    file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
    return {
        'name': filename,
        'size': file_size,
        'creation_time': file_creation_time
    }

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            logging.error('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            logging.error('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{filename}"
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File successfully uploaded')
                logging.info(f'File {filename} successfully uploaded')
            except Exception as e:
                flash('File upload failed')
                logging.error(f'File upload failed: {e}')
            return redirect(url_for('upload_file'))
        else:
            flash('File type not allowed')
            logging.warning('File type not allowed')
            return redirect(request.url)
    files = [get_file_properties(file, app.config['UPLOAD_FOLDER']) for file in os.listdir(app.config['UPLOAD_FOLDER'])]
    clipboard_files = [get_file_properties(file, app.config['CLIPBOARD_FOLDER']) for file in os.listdir(app.config['CLIPBOARD_FOLDER'])]
    return render_template('index.html', files=files, clipboard_files=clipboard_files, allowed_extensions=ALLOWED_EXTENSIONS)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/clipboard/<filename>')
def clipboard_file(filename):
    return send_from_directory(app.config['CLIPBOARD_FOLDER'], filename)

@app.route('/clipboard', methods=['POST'])
def clipboard():
    data = request.form['clipboard_data']
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = f"clipboard_{uuid.uuid4()}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['CLIPBOARD_FOLDER'], filename))
            return jsonify({'status': 'success', 'message': 'Image saved', 'filename': filename})
    else:
        filename = f"clipboard_{uuid.uuid4()}.txt"
        with open(os.path.join(app.config['CLIPBOARD_FOLDER'], filename), 'w') as f:
            f.write(data)
        return jsonify({'status': 'success', 'message': 'Text saved', 'filename': filename})

def cleanup_files():
    now = datetime.now()
    for folder in [UPLOAD_FOLDER, CLIPBOARD_FOLDER]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if now - file_creation_time > timedelta(days=1):
                os.remove(file_path)
                logging.info(f'Removed file {filename}')

# Setup and start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_files, trigger="interval", hours=24)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3010, debug=True)
