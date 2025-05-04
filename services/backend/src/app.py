"""The main application entry point for the image upload server.

This module defines the UploadHandler for serving HTTP requests, including routes for:
    - Health check (/)
    - Image listing (/upload/)
    - Image upload (/upload/)
    - Image deletion (/upload/<filename>)

It also provides logic to start multiple server processes using multiprocessing.

Side effects:
    - Binds and serves HTTP servers on configured ports.
    - Writes uploaded images to disk.
    - Deletes files from disk.
    - Logs actions and errors via configured logger.
"""

import json, os
from multiprocessing import Process, current_process
from typing import cast
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

from python_multipart import parse_form

from exceptions.api_errors import APIError, MultiFilesUploadError
from handlers.files import list_uploaded_images
from handlers.upload import handle_uploaded_file
from interfaces.protocols import RequestHandlerFactory
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__)

class UploadHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests related to file uploads, listing, and deletion.

        Routes:
            GET / → Healthcheck.
            GET /upload/ → List all uploaded image files.
            POST /upload/ → Upload a single image file.
            DELETE /upload/<filename> → Delete the specified image.

        Use:
            - Dynamic dispatch based on `routes_get`, `routes_post`, and `routes_delete`.
    """

    routes_get = {
        "/": "_handle_get_root",
        "/upload/": "_handle_get_uploads"
    }

    routes_post = {
        "/upload/": "_handle_post_upload"
    }

    routes_delete = {
        "/upload/": "_handle_delete_upload"
    }

    def _send_json_error(self, status_code: int, message: str) -> None:
        """Sends a JSON error response and logs the message.

                Args:
                    status_code (int): HTTP status code to return.
                    message (str): Error message to return and log.

                Side effects:
                    - Logs the error or warning.
                    - Writes JSON response to the client.
        """

        if status_code >= 500:
            logger.error(f"{self.command} {self.path} -> {status_code}: {message}")
        else:
            logger.warning(f"{self.command} {self.path} -> {status_code}: {message}")

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"detail": message}
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self) -> None:
        """Handles GET requests and dispatches them based on the route."""

        self._handle_request(self.routes_get)

    def do_POST(self) -> None:
        """Handles POST requests and dispatches them based on the route."""

        self._handle_request(self.routes_post)

    def do_DELETE(self) -> None:
        """Handles DELETE requests and dispatches them based on the route."""

    def _handle_request(self, routes: dict[str, str]) -> None:
        """Resolves path to appropriate handler method and calls it.

                Args:
                    routes (dict[str, str]): Mapping of path to handler method names.

                Side effects:
                    - Calls appropriate handler method.
                    - Sends 404 or 500 response if handler is not found or not implemented.
        """

        handler_name = routes.get(self.path)
        if not handler_name:
            for route_prefix, candidate_handler in routes.items():
                if self.path.startswith(route_prefix):
                    handler_name = candidate_handler
                    break

        if not handler_name:
            self._send_json_error(404, "Not found")
            return

        handler()

    def _handle_get_root(self) -> None:
        """Handles healthcheck at GET /."""

        logger.info("Healthcheck endpoint hit: /")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Welcome to the Image Hosting Server"}).encode())

    def _handle_get_upload(self) -> None:
        """Returns a list of uploaded images as JSON.

                Side effects:
                    - Reads image directory.
                    - Sends either an HTTP response or an error.
        """

        try:
            files = list_uploaded_images()
        except FileNotFoundError:
            self._send_json_error(500, "Images directory not found.")
            return
        except PermissionError:
            self._send_json_error(500, "Permission denied.")
            return

        if not files:
            self._send_json_error(404, "No images found.")
            return

        logger.info(f"Returned list of {len(files)} uploaded images.")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(files).encode())

    def _handle_post_upload(self) -> None:
        """Processes and saves an uploaded file.

                Side effects:
                    - Parses multipart form data.
                    - Validates and saves uploaded file to disk.
                    - Sends response or error.
        """

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json_error(400, "Bad request: Expected 'multipart/form-data'.")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        headers = {
            "Content-Type": content_type,
            "Content-Length": str(content_length)
        }

        files = []

        def on_file(file):
            if len(files) >= 1:
                raise MultiFilesUploadError()
            files.append(file)

        try:
            saved_file_info = handle_uploaded_file(files[0])
        except APIError as e:
            self._send_json_error(e.status_code, e.message)
            return

        logger.info(f"File '{saved_file_info['filename']}' uploaded successfully.")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(
            f"{{'filename': '{saved_file_info['filename']}',"
            f" 'url': '{saved_file_info['url']}'}}".encode()
        )

    def _handle_delete_upload(self) -> None:
        """Deletes a file by its name from the upload directory.

                Side effects:
                    - Deletes a file from the filesystem.
                    - Sends a JSON response or an error.
        """

        if not self.path.startswith("/upload/"):
            self._send_json_error(404, "Not found")
            return

        filename = self.path[len("/upload/"):]

        if not filename:
            self._send_json_error(400, "Filename not provided.")
            return

        filename = os.path.join(config.IMAGES_DIR, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in config.SUPPORTED_FORMATS:
            self._send_json_error(400, "Unsupported file format.")
            return

        if not os.path.isfile(filename):
            self._send_json_error(404, "File not found.")
            return

        try:
            os.remove(filename)
        except PermissionError:
            self._send_json_error(500, "Permission denied.")
            return
        except Exception as e:
            self._send_json_error(500, f"Internal server error: {str(e)}")
            return

        logger.info(f"File '{filename}' deleted successfully.")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": f"File '{filename}' deleted successfully."}).encode())

def run_server_on_port(port: int) -> None:
    """Starts a single HTTP server instance on the specified port.

        Args:
            port (int): The port number to bind the HTTP server to.

        Side effects:
            - Starts blocking HTTP server loop.
            - Logs process and port information.
    """

    current_process().name = f"worker-{port}"
    logger.info(f"Starting HTTP server on http://0.0.0.0:{port}")
    server = HTTPServer(("0.0.0.0", port), cast(RequestHandlerFactory, UploadHandler))
    server.serve_forever()

def run(workers: int = 1, start_port: int = 8000) -> None:
    """Starts multiple server worker processes for concurrent handling.

        Args:
            workers (int): Number of worker processes to spawn.
            start_port (int): Starting port number for workers.

        Side effects:
            - Launches `workers` processes each listening on a unique port.
            - Logs worker startup.
    """

    for worker in range(workers):
        port = start_port + worker
        p = Process(target=run_server_on_port, args=(port,))
        p.start()
        logger.info(f"Starting worker {worker + 1} on port {port}")


if __name__ == "__main__":
    run(workers=config.WEB_SERVER_WORKERS, start_port=config.WEB_SERVER_START_PORT)