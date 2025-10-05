
# Скрипт, который скачивает все репозитории и гисты пользователя на Github
# Модули: urllib.request, json, os, subprocess, getopt (используется встроенный HTTP-API GitHub и системные вызовы git clone)
'''
Утилита командной строки, которую запускаешь с указанием имени пользователя GitHub и каталога назначения — и скрипт
скачивает все публичные репозитории и гисты этого пользователя. Полезно для бэкапа кода, архивации своих проектов или
просмотра чужих проектов локально.
- Получает список репозиториев пользователя через GitHub API
- Клонирует каждый репозиторий командой git clone
- Получает список гистов и клонирует их как отдельные git-репо
-
 Кладёт всё это в структуру папок: repos/ и gists/ в указанном каталоге
'''

import getopt
import json
import os
import subprocess
import sys
from urllib.request import urlopen

def Usage():
    print("Usage: %s -u <github user> -d <directory>" % sys.argv[0])

def main():
    githubUser = ''
    destDirectory = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:d:h")
        for o, a in opts:
            if o == '-u':
                githubUser = a
            elif o == '-d':
                destDirectory = a
            elif o == '-h':
                Usage()
                sys.exit(0)
    except getopt.GetoptError as e:
        print(str(e))
        Usage()
        sys.exit(2)

    if not githubUser or not destDirectory:
        print("Use -u for GitHub user, -d for destination dir")
        Usage()
        sys.exit(0)

    reposLink = f"https://api.github.com/users/{githubUser}/repos?type=all&per_page=100&page=1"
    f = urlopen(reposLink)
    repos = json.loads(f.readline())
    print("Total repos:", len(repos))

    os.makedirs(destDirectory, exist_ok=True)
    os.chdir(destDirectory)

    os.makedirs("repos", exist_ok=True)
    os.makedirs("gists", exist_ok=True)

    # Скачиваем репозитории
    os.chdir("repos")
    for repo in repos:
        print("Cloning:", repo['html_url'])
        subprocess.call(['git', 'clone', repo['html_url']])

    # Скачиваем гисты
    os.chdir("../gists")
    gistsLink = f"https://api.github.com/users/{githubUser}/gists"
    f = urlopen(gistsLink)
    gists = json.loads(f.readline())
    print("Total gists:", len(gists))
    for gist in gists:
        print("Cloning gist:", gist.get('git_pull_url'))
        subprocess.call(['git', 'clone', gist.get('git_pull_url')])

if __name__ == "__main__":
    main()
