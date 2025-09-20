# conda activate allpy311

# Визуально эмулирует загрузочный экран ZX Spectrum :)

import pygame
import sys
import random
import numpy as np
import time

pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

W, H = 600, 400
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

def beep(freq=800, dur=50):
    sample_rate = 22050
    n = int(sample_rate * dur / 1000)
    arr = (np.sin(2 * np.pi * np.arange(n) * freq / sample_rate) * 32767).astype(np.int16)
    sound = pygame.mixer.Sound(buffer=arr.tobytes())
    sound.play()
    pygame.time.delay(dur)

colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)]

for _ in range(120):
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    rect_h = random.randint(5, 30)
    y = random.randint(0, H - rect_h)
    color = random.choice(colors)
    pygame.draw.rect(screen, color, (0, y, W, rect_h))
    pygame.display.flip()
    beep(random.randint(300, 1200), 40)
    time.sleep(0.02)

time.sleep(1)
pygame.quit()