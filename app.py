import webbrowser
from threading import Timer
from digital_stamp import app  # Import your Flask app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/stamp")  # default page

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run()
