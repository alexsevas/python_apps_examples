# Автоматическое сжатие и архивирование логов
#
# * старые .log → архивируются в .gz;
# * старше keep_days удаляются;
# * экономит место и сохраняет историю.
#
# Всё на стандартной библиотеке — ничего ставить не нужно


import gzip, shutil, os, glob, datetime

def rotate_logs(path="logs/*.log", keep_days=7):
    now = datetime.datetime.now()
    for file in glob.glob(path):
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file))
        if (now - mtime).days > 0:
            gz = f"{file}.{mtime:%Y%m%d}.gz"
            with open(file, "rb") as f_in, gzip.open(gz, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            open(file, "w").close()  # truncate log
    for gz in glob.glob("logs/*.gz"):
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(gz))
        if (now - mtime).days > keep_days:
            os.remove(gz)
