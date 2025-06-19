📷 Image Hosting Server v1.0

A lightweight containerized service for uploading, viewing, and managing images via a browser interface.
It features a drag-and-drop uploader, automatic URL generation, image listing with delete support, and persistent logging—all powered by a clean backend plus frontend separation. The static is stored with Nginx, and everything is managed with Docker Compose.
✨ Table of Contents

    Overview
    Features
    Installation
    Usage
    Project Structure
    Tech Stack

📌 Overview

This project is a mini fullstack service built for uploading and sharing images through a clean UI.
It includes:

    A backend server written in Python (no frameworks, just http.server)
    A modern frontend UI with drag-and-drop support
    Nginx reverse proxy with multi-port load balancing
    Logging of all backend and access events
    Simple REST API with routes for uploading, listing, and deleting images

All components are containerized and orchestrated via docker-compose.
🚀 Features

    📤 Upload via Drag & Drop or Button
    Users can upload .jpg, .png, or .gif images by clicking a button or dragging files into the UI.

    🧾 Image Listing Table
    Uploaded images are listed in a styled table with preview icons and full shareable URLs.

    🗑 Delete Support
    Each image row includes a trash icon to delete the file immediately from the server.

    🔁 Live Tab Switching
    The UI allows switching between "Upload" and "Images" views without reloading the page.

    🧠 Error Feedback
    All user errors (incorrect type, large size, network issues) are shown immediately on-screen.

    📦 Dockerized Deployment
    The entire stack runs with a single command using Docker Compose.

⚙️ Installation

Clone the repository and start the containers:

git clone https://github.com/gxneshx/Second_Project_v1.0.git
cd Second_Project_v1.0
docker-compose up --build

Before running the server, configure the environment variables for the backend:

    Navigate to the backend service directory:

    cd services/backend

    Copy the sample file and adjust the values as needed:

    cp .env.sample .env

    Sample .env.sample:

    # Directory where uploaded images will be stored 
    IMAGES_DIR=/usr/src/images

    # Directory where log files will be written
    LOG_DIR=/var/log

    # Number of worker processes to spawn for HTTP server (10 is an example)
    WEB_SERVER_WORKERS=10

    # Starting port number for worker processes (each worker gets a unique port)
    WEB_SERVER_START_PORT=8000

Make sure the IMAGES_DIR and LOG_DIR match the volume paths defined in docker-compose.yml.

Then visit:
http://localhost


📂 Usage
Web UI

    Open the browser and go to http://localhost (start page)
    Click the only blue button - it gets you to the main page for uploading images
    Drag and drop or select a file to upload
    Copy the generated image URL
    Switch to the "Images" tab to see all uploaded files
    Click the trash icon to delete any file or copy the file name/url manually to use further


📁 Project Structure

.
├── README.md
├── docker-compose.yml
├── images/                      # Uploaded files stored here (mounted volume)
├── logs/
│   ├── app.log                  # Backend logs
│   └── nginx/
│       ├── access.log
│       └── error.log
└── services/
    ├── backend/
    │   ├── Dockerfile
    │   ├── poetry.lock
    │   ├── pyproject.toml
    │   ├── .env                  # Environmental variables
    │   └── src/
    │       ├── app.py
    │       ├── exceptions/
    │       │   └── api_errors.py
    │       ├── handlers/
    │       │   ├── files.py
    │       │   └── upload.py
    │       ├── interfaces/
    │       │   └── protocols.py
    │       └── settings/
    │           ├── config.py
    │           └── logging_config.py
    ├── frontend/
    │   ├── index.html
    │   ├── upload.html
    │   ├── css/
    │   │   ├── index.css
    │   │   └── upload.css
    │   ├── js/
    │   │   ├── upload.js
    │   │   ├── tabs.js
    │   │   └── index.js
    │   ├── base_images/
    │       ├── 1.svg ... 5.svg
    │       └── ico/
    │           ├── delete_trash_icon.png
    │           └── fav.png
    │        
    └── nginx/
        └── nginx.conf

🧰 Tech Stack

Layer 	Technology
Backend 	Python http.server, custom routing, custom logging
Frontend 	HTML, CSS, JavaScript
Web Server 	Nginx
Logging 	Python Logging + Nginx logs
Packaging 	Docker, Docker Compose
Styling 	Custom CSS (no frameworks)