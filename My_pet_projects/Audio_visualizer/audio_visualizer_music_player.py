# conda activate allpy310

# pip install PyQt6 vispy numpy sounddevice pygame soundfile scipy

import sys
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QFileDialog, QLabel, QHBoxLayout
)
from PyQt6.QtCore import QTimer
import pygame
from vispy import scene

# Глобальные параметры
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024
pygame.mixer.init(frequency=SAMPLE_RATE, channels=2, buffer=BLOCK_SIZE)


class AudioVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Visualizer with Player")
        self.setGeometry(100, 100, 800, 600)

        # VisPy Canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black')
        self.view = self.canvas.central_widget.add_view()
        self.plot = scene.Line(pos=np.zeros((100, 2)), parent=self.view.scene, color='cyan', width=2)
        self.view.camera = 'panzoom'
        self.view.camera.set_range(x=(-1, 1), y=(-1, 1))

        # Элементы управления
        self.file_label = QLabel("Файл не выбран")
        self.play_btn = QPushButton("▶️ Воспроизвести")
        self.pause_btn = QPushButton("⏸ Пауза")
        self.stop_btn = QPushButton("⏹ Стоп")
        self.switch_btn = QPushButton("🔁 Сменить режим")

        self.play_btn.clicked.connect(self.play_audio)
        self.pause_btn.clicked.connect(self.pause_audio)
        self.stop_btn.clicked.connect(self.stop_audio)
        self.switch_btn.clicked.connect(self.switch_mode)

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.switch_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.canvas.native)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Состояние
        self.mode = 0
        self.audio_data = None
        self.current_pos = 0
        self.is_playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.timer.setInterval(int(1000 * BLOCK_SIZE / SAMPLE_RATE))  # ~23 мс для 1024/44100

        # Загрузка файла
        self.load_file()

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите аудиофайл", "", "Аудио (*.mp3 *.wav *.ogg *.flac)"
        )
        if not file_path:
            sys.exit(0)  # если файл не выбран — выходим

        self.file_label.setText(f"Файл: {file_path.split('/')[-1]}")
        pygame.mixer.music.load(file_path)

        # Предварительная загрузка данных для визуализации (через sounddevice не будем слушать микрофон!)
        # Мы будем читать данные из pygame.mixer или через отдельную загрузку с помощью librosa/pydub
        # Для простоты — воспроизводим через pygame, а данные для визуализации будем брать из numpy-буфера

        # Альтернатива: использовать soundfile или librosa для загрузки массива
        try:
            import soundfile as sf
            self.audio_data, sr = sf.read(file_path)
            if self.audio_data.ndim > 1:
                self.audio_data = np.mean(self.audio_data, axis=1)  # стерео → моно
            # ресемплируем, если нужно
            if sr != SAMPLE_RATE:
                from scipy.signal import resample
                num_samples = int(len(self.audio_data) * SAMPLE_RATE / sr)
                self.audio_data = resample(self.audio_data, num_samples)
        except ImportError:
            print("Установите soundfile и scipy для загрузки аудио: pip install soundfile scipy")
            sys.exit(1)

        print(f"Загружено {len(self.audio_data)} сэмплов")

    def play_audio(self):
        if not self.is_playing:
            pygame.mixer.music.play()
            self.current_pos = 0
            self.timer.start()
            self.is_playing = True

    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.timer.stop()
        else:
            pygame.mixer.music.unpause()
            self.timer.start()

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.timer.stop()
        self.current_pos = 0
        self.is_playing = False
        # Сбросим визуализацию
        self.plot.set_data(np.zeros((100, 2)))

    def switch_mode(self):
        self.mode = (self.mode + 1) % 3
        print(f"Режим: {self.mode}")

    def update_visualization(self):
        if self.audio_data is None:
            return

        # Берём следующий блок данных
        start = self.current_pos
        end = start + BLOCK_SIZE
        if end > len(self.audio_data):
            # Достигли конца
            self.stop_audio()
            return

        samples = self.audio_data[start:end]
        self.current_pos = end

        # FFT
        fft_vals = np.abs(np.fft.rfft(samples))[:200]

        if self.mode == 0:  # Осциллограф
            y = samples[:100]
            x = np.linspace(-1, 1, len(y))
            self.plot.set_data(np.column_stack([x, y]))
        elif self.mode == 1:  # Спектр
            x = np.linspace(-1, 1, len(fft_vals))
            norm_fft = fft_vals / (np.max(fft_vals) + 1e-8)
            self.plot.set_data(np.column_stack([x, norm_fft]))
        elif self.mode == 2:  # Радиальная
            angles = np.linspace(0, 2 * np.pi, len(fft_vals))
            r = fft_vals / (np.max(fft_vals) + 1e-8)
            x = r * np.cos(angles)
            y = r * np.sin(angles)
            self.plot.set_data(np.column_stack([x, y]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = AudioVisualizer()
    win.show()
    sys.exit(app.exec())