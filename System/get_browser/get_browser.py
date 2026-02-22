# Определение браузера по умолчанию в Windows


from winreg import OpenKey, HKEY_CURRENT_USER, HKEY_CLASSES_ROOT, QueryValueEx


def get_browser_command() -> str:
    path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.html\UserChoice"
    with OpenKey(HKEY_CURRENT_USER, path) as key:
        browser_id = QueryValueEx(key, 'Progid')[0]

    path = browser_id + r"\shell\open\command"
    with OpenKey(HKEY_CLASSES_ROOT, path) as key:
        command = QueryValueEx(key, '')[0]

    return command


if __name__ == '__main__':
    print(get_browser_command())
    # "C:\Program Files\Mozilla Firefox\firefox.exe" -osint -url "%1"
