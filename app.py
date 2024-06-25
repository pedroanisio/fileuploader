from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
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
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'pst'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Load SECRET_KEY from environment

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_properties(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
    files = [get_file_properties(file) for file in os.listdir(app.config['UPLOAD_FOLDER'])]
    return render_template('index.html', files=files, allowed_extensions=ALLOWED_EXTENSIONS)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def cleanup_files():
    now = datetime.now()
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
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

