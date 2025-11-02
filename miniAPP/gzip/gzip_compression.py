# conda activate allpy311

# Сжатие файлов в архивы gz с помощью gzip, и shutil. Понадобятся функции gzip.open и shutil.copyfileobj

import gzip
import shutil

def compress_file(input_file, output_file):
  with open(input_file, 'rb') as f_in:
    with gzip.open(output_file, 'wb') as f_out:
      shutil.copyfileobj(f_in, f_out)

compress_file('bookmarks.txt', 'bookmarks.txt.gz')
