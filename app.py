import webview
import threading
import os, sys
from flask import Flask

# Import the blueprint from your digital_stamp.py
from digital_stamp import digital_stamp_bp

# Determine base path for PyInstaller
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller temp folder
else:
    base_path = os.path.abspath(".")

# Initialize Flask app
# We explicitly set template_folder and static_folder at the app level too,
# pointing them to the directories that PyInstaller will create.
app = Flask(__name__,
            template_folder=os.path.join(base_path, "templates"),
            static_folder=os.path.join(base_path, "static"))
app.secret_key = 'seiko_electric_demo_secret_key' # Keep your secret key

# Register the blueprint
app.register_blueprint(digital_stamp_bp)

# Function to start the Flask server
def start_server():
    # Use a non-default port if 5000 is often taken, e.g., 8000
    # or you can make the port dynamic.
    app.run(port=5000)

# Main function to set up and run the desktop app
def main():

    # Start the Flask server in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True  # Allows the thread to exit when the main program exits
    t.start()

    # Create the PyWebView window
    # The URL points to your Flask app running locally
    webview.create_window('Digital Stamp System', 'http://127.0.0.1:5000', min_size=(900, 700))
    webview.start() # This call blocks until the window is closed

if __name__ == '__main__':
    main()