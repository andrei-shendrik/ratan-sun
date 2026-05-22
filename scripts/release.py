import subprocess
import sys
import tomllib
from pathlib import Path


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

def get_project_version() -> str:
    toml_path = Path("pyproject.toml")
    if not toml_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
        return data["project"]["version"]

def get_git_tags() -> list[str]:
    """список тегов в репозитории"""
    output = run_cmd("git tag", capture_output=True)
    return [tag.strip() for tag in output.split("\n") if tag.strip()]

def get_latest_tag() -> str:
    """последний тег"""
    output = run_cmd("git tag --sort=-v:refname", capture_output=True)
    tags = [tag.strip() for tag in output.split("\n") if tag.strip()]
    return tags[0] if tags else "No tags found"

def main():
    print("*** Release script ***")

    run_cmd("git fetch --tags", capture_output=False)
    latest_tag = get_latest_tag()
    print(f"Latest tag version in repository: {latest_tag}")

    version = input("Enter the new version (e.g. '1.0.0'): ").strip()
    target_tag = None
    if version.startswith('v'):
        target_tag = f"{version}"
    else:
        target_tag = f"v{version}"

    if target_tag is None:
        return

    existing_tags = get_git_tags()
    if target_tag in existing_tags:
        print(f"Error: tag {target_tag} already exists in repository")
        sys.exit(1)

    commit_message = input(f"Enter commit message for release {target_tag}: ").strip()

    if not commit_message:
        print("Error: commit message cannot be empty")
        sys.exit(1)

    confirm = input(
        f"\nThe following actions will be performed:\n-Merge develop -> main\n- Commit: '{commit_message}\n- Tag: {target_tag}\n- Push -> GitHub\nContinue? (y/n): ")
    if confirm.lower() != 'y':
        print("Canceled")
        sys.exit(0)

    run_cmd("git checkout develop")
    run_cmd("git pull origin develop")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{commit_message}"')
    run_cmd("git push origin develop")

    run_cmd("git checkout main")
    run_cmd("git pull origin main")
    run_cmd(f'git merge --no-ff develop -m "Merge develop into main for release {target_tag}"')
    run_cmd("git push origin main")

    run_cmd(f'git tag -a {target_tag} -m "Release version {version}"')
    run_cmd("git push origin --tags")

    run_cmd("git checkout develop")

    print(f"\nRelease {target_tag} successfully completed and pushed to repository")


if __name__ == "__main__":
    main()