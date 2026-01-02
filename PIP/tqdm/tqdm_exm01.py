


from tqdm import tqdm
import time

# Простой пример с range
for i in tqdm(range(100)):
    time.sleep(0.02)  # Имитация длительной операции


# С ручным обновлением
with tqdm(total=100) as pbar:
    for i in range(10):
        time.sleep(0.1)
        pbar.update(10) # Обновление индикатора на 10 единиц


# С описанием
for i in tqdm(range(100), desc="Обработка данных"):
    time.sleep(0.02)

# Вложенные циклы
from tqdm import trange
for i in trange(4, desc="1st loop"):
    for j in trange(5, desc="2nd loop", leave=False):
        for k in trange(50, desc="3rd loop", leave=False):
            time.sleep(0.001)

# С pandas
import pandas as pd
df = pd.DataFrame({'a': range(10000)})

# Применение tqdm к pandas DataFrame (apply с progress_apply)
tqdm.pandas() #  Необходимо для progress_apply
df['b'] = df['a'].progress_apply(lambda x: x*x) #  Индикатор выполнения для apply



# Пример с файлами
import os
with open("large_file.txt", "w") as f:
    for i in trange(10000, desc="Создание файла"):
        f.write("This is a line of text.\n")


with open("large_file.txt", "r") as f:
    for line in tqdm(f, total=os.path.getsize("large_file.txt"), unit="B", unit_scale=True, unit_divisor=1024, desc="Чтение файла"):
        # Обработка каждой строки файла
        pass
