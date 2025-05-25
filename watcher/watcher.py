from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
import sys


print("✅ subprocess で起動する Python:", sys.executable)

VENV_PYTHON = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
BOT_MAIN = os.path.join("bot", "main.py")

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = self.start_bot()

    def start_bot(self):
        print("🚀 Botを起動します...")
        return subprocess.Popen([VENV_PYTHON, BOT_MAIN])

    def on_modified(self, event):
        if event.src_path.endswith((".py",)):  # .pyファイル全体を対象にする
            print(f"🔄 {event.src_path} が変更されました。再起動します。")
            self.process.kill()
            self.process = self.start_bot()



def start():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path="bot", recursive=True)
    observer.start()
    print("👀 bot/ 配下を監視中...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 停止します")
        observer.stop()
        event_handler.process.kill()
    observer.join()
