# File and Clipboard Manager

File and Clipboard Manager is a web application that allows users to upload files and manage clipboard content. Users can drag and drop files for upload, view and download uploaded files, and manage clipboard text and images. Clipboard text content can be viewed in an accordion-style interface, and users can easily copy text content with a click.

## Features

- Drag and drop file upload
- View and download uploaded files
- Clipboard text and image management
- View text content in an accordion-style interface
- Copy text content with a click
- Files are automatically cleaned up every 24 hours

## Technology Stack

- Flask (Python web framework)
- APScheduler (Python library for scheduling tasks)
- Bootstrap (CSS framework for responsive design)
- JavaScript for client-side functionality

## Setup and Installation

### Prerequisites

- Docker
- Python 3.12
- Pip

### Environment Variables

Create a `.env` file in the project root directory with the following content:


### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/pedroanisio/file-and-clipboard-manager.git
    cd file-and-clipboard-manager
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Build and run the Docker container:**
    ```sh
    docker build -t file-upload-app .
    docker run -p 3010:3010 file-upload-app
    ```

### Usage

- Open your web browser and navigate to `http://localhost:3010`.
- Drag and drop files into the designated area to upload.
- View, download, and manage uploaded files.
- Paste text into the clipboard section and save it. View, download, and copy clipboard text content.

### File Structure

```
file-and-clipboard-manager/
├── app.py
├── Dockerfile
├── generate_secret.sh
├── requirements.txt
├── static/
│   └── styles.css
└── templates/
    └── index.html
```

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

### License

This project is licensed under the MIT License.

### Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [Bootstrap](https://getbootstrap.com/)
```
