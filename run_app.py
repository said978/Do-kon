import os
import sys
import webbrowser
import threading
import time

# PyInstaller va joriy papka yo'llarini qo'shish
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


    # Brauzerni avtomatik ochish
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:8000/api/sales/pos/')


    threading.Thread(target=open_browser, daemon=True).start()

    from django.core.management import execute_from_command_line

    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload'])