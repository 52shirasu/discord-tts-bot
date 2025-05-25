# application.py の例（watcherを起動）
import subprocess
import sys
import os

# ファイル監視などを続けて実行
from watcher import watcher
watcher.start()
