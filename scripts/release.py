import subprocess
import sys


def run_cmd(command: list[str] | str, capture_output: bool = False) -> str:
    """
    Если capture_output=True, возвращает текст вывода (без вывода на экран).
    Если capture_output=False, печатает процесс в консоль.
    """
    is_shell = isinstance(command, str)
    cmd_str = command if is_shell else " ".join(command)
    print(f"Executing: {cmd_str}")

    result = subprocess.run(
        command,
        shell=is_shell,
        capture_output=capture_output,
        text=True
    )

    if result.returncode != 0:
        print(f"\nERROR: Command failed with code {result.returncode}")
        if capture_output:
            print(f"Error output:\n{result.stderr}")
        print("Please fix the issue manually in Git and try again.")
        sys.exit(1)

    return result.stdout.strip() if capture_output else ""

def get_git_tags() -> list[str]:
    """список тегов в репозитории"""
    output = run_cmd("git tag", capture_output=True)
    return [tag.strip() for tag in output.split("\n") if tag.strip()]

def get_latest_tag() -> str:
    """последний тег"""
    output = run_cmd("git tag --sort=-v:refname", capture_output=True)
    tags = [tag.strip() for tag in output.split("\n") if tag.strip()]
    return tags[0] if tags else "No tags found"

def has_uncommitted_changes() -> bool:
    """есть ли измененные файлы в рабочей директории"""
    output = run_cmd("git status --porcelain", capture_output=True)
    return bool(output)

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

    run_cmd("git checkout develop")
    run_cmd("git pull origin develop")

    needs_commit = has_uncommitted_changes()
    commit_message = ""

    if needs_commit:
        print("\nUncommitted changes detected in develop")
        commit_message = input(f"Enter commit message for develop: ").strip()

        if not commit_message:
            print("Error: commit message cannot be empty")
            sys.exit(1)
    else:
        print("\nWorking tree is clean. No new commit needed in develop")

    merge_msg = f"Merge develop into main for release {target_tag}"

    print(f"\nThe following actions will be performed:")
    if needs_commit:
        print(f"  - Commit changes to develop: '{commit_message}'")
    print(f"  - Merge develop -> main (--no-ff): '{merge_msg}'")
    print(f"  - Tag main: {target_tag}")
    print(f"  - Merge main -> develop")
    print(f"  - Push -> GitHub")

    confirm = input("\nContinue? (y/n): ").strip().lower()
    if confirm.lower() != 'y':
        print("Canceled")
        sys.exit(0)

    # commit develop
    if needs_commit:
        run_cmd("git add -A")
        run_cmd(["git", "commit", "-m", commit_message])
    run_cmd("git push origin develop")

    # release main
    run_cmd("git checkout main")
    run_cmd("git pull origin main")
    run_cmd(["git", "merge", "--no-ff", "develop", "-m", merge_msg])
    run_cmd("git push origin main")

    # tags
    tag_msg = f"Release version {version}"
    run_cmd(["git", "tag", "-a", target_tag, "-m", tag_msg])
    run_cmd("git push origin --tags")

    # sync
    run_cmd("git checkout develop")
    run_cmd("git merge main")
    run_cmd("git push origin develop")

    print(f"\nRelease {target_tag} successfully completed and pushed to repository")

if __name__ == "__main__":
    main()