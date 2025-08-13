import webbrowser
from threading import Timer
from digital_stamp import app  # import your Flask app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Open browser after 1 second
    Timer(1, open_browser).start()
    app.run()
