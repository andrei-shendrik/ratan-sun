import subprocess
import sys

"""
    Скрипт деплоя на продакшн сервер. Для его работы необходимо установить утилиту gh. Она скачивается с сайта github.
"""

def get_latest_tag() -> str:
    """последний тег"""
    output = run_cmd("git tag --sort=-v:refname", capture_output=True)
    tags = [tag.strip() for tag in output.split("\n") if tag.strip()]
    return tags[0] if tags else "No tags found"


def run_cmd(command: str, capture_output: bool = False) -> str:
    """
    Если capture_output=True, возвращает текст вывода (без вывода на экран).
    Если capture_output=False, печатает процесс в консоль.
    """
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)

    if result.returncode != 0:
        print(f"Error: '{command}' terminated with code {result.returncode}")
        if capture_output:
            print(f"Error: {result.stderr}")
        sys.exit(1)

    return result.stdout.strip() if capture_output else ""

def main():
    print("*** Deploy script ***")

    run_cmd("git fetch --tags", capture_output=False)
    latest_tag = get_latest_tag()
    print(f"Latest tag version in repository: {latest_tag}")

    deploy = input("\nRun the deploy to production server (y/n): ")
    if deploy.lower() == 'y':
        run_cmd(f"gh workflow run deploy.yml -f") # version={version}
        print("Deploy has been started. Check GitHub Actions for status")
    sys.exit(0)

if __name__ == "__main__":
    main()