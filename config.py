import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")


SECRET_KEY = "your_secret_key"
