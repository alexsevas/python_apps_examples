# conda activate allpy311
# pip install watchdog


# Авто-сортировщик файлов в реальном времени
# Скрипт в фоне следит за папкой Downloads и сразу раскладывает новые файлы по папкам.


import time, shutil, pathlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DOWNLOADS = pathlib.Path.home() / "Downloads"
TARGETS = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Docs": [".pdf", ".docx", ".txt"],
    "Archives": [".zip", ".rar", ".tar", ".gz"],
    "Music": [".mp3", ".wav"],
}

class SortHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file = pathlib.Path(event.src_path)
            ext = file.suffix.lower()
            for folder, exts in TARGETS.items():
                if ext in exts:
                    dest = DOWNLOADS / folder
                    dest.mkdir(exist_ok=True)
                    shutil.move(str(file), dest / file.name)
                    print(f"📦 {file.name} → {folder}")
                    break

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(SortHandler(), str(DOWNLOADS), recursive=False)
    observer.start()
    print("👀 Следим за папкой Downloads...")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
