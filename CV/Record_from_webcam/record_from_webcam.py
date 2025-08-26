# conda activate allpy311

# pip install opencv-python

'''
Запись видео с веб‑камеры.

Чистый скрипт на OpenCV:
-подключается к веб‑камере,
-показывает превью в реальном времени (файл сохраняется в: records/vid.mp4),
-пишет MP4 с нужным разрешением и FPS,
-выходит по клавише Q,
-код структурирован на функции, есть @dataclass для настроек — бери, редактируй и встраивай в свой проект.
'''

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional

import cv2

@dataclass(frozen=True)
class CaptureConfig:
    """Настройки захвата видео с веб‑камеры."""
    device_index: int = 0       # индекс камеры (0 — встроенная)
    width: int = 640            # ширина кадра
    height: int = 480           # высота кадра
    fps: int = 20               # кадров в секунду
    fourcc: str = "mp4v"        # кодек для MP4: mp4v, для AVI: XVID

def create_capture(cfg: CaptureConfig) -> cv2.VideoCapture:
    """Создаёт и настраивает объект VideoCapture."""
    cap = cv2.VideoCapture(cfg.device_index)
    if not cap.isOpened():
        raise RuntimeError("Не удалось открыть веб‑камеру")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
    cap.set(cv2.CAP_PROP_FPS, cfg.fps)
    return cap

def create_writer(output_path: Path, cfg: CaptureConfig) -> cv2.VideoWriter:
    """Создаёт объект записи видео (VideoWriter)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*cfg.fourcc)
    writer = cv2.VideoWriter(str(output_path), fourcc, cfg.fps, (cfg.width, cfg.height))
    if not writer.isOpened():
        raise RuntimeError(f"Не удалось создать файл для записи: {output_path}")
    return writer

def record_from_webcam(
    output_path: Path,
    cfg: CaptureConfig = CaptureConfig(),
    window_title: str = "Video",
) -> Tuple[bool, Optional[str]]:
    """
    Захватывает поток с веб‑камеры, показывает превью и пишет в файл.
    Возвращает (успех, сообщение_ошибки).
    Остановка по клавише 'q'.
    """
    try:
        cap = create_capture(cfg)
        writer = create_writer(output_path, cfg)
    except Exception as e:
        return False, str(e)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                return False, "Не удалось прочитать кадр с камеры"

            writer.write(frame)
            cv2.imshow(window_title, frame)

            # выход по 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        return True, None
    finally:
        cap.release()
        writer.release()
        cv2.destroyAllWindows()



def main() -> None:
    cfg = CaptureConfig(
        device_index=0,
        width=640,
        height=480,
        fps=20,
        fourcc="mp4v",  # для .mp4; можно 'XVID' для .avi
    )
    ok, err = record_from_webcam(Path("records/vid.mp4"), cfg)
    if ok:
        print("✅ Запись завершена. Файл: records/vid.mp4")
    else:
        print(f"❌ Ошибка: {err}")


if __name__ == "__main__":
    main()
