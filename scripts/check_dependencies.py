import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_command(command: str) -> bool:
    """Выполняет команду и возвращает True, если успешно, иначе False"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=PROJECT_ROOT)
    return result.returncode == 0

def main():
    success = True

    commands = [
        "deptry apps/bin2fits-fast-acquisition-1-3ghz-nodb --config apps/bin2fits-fast-acquisition-1-3ghz-nodb/pyproject.toml",
        "deptry libs/ratanpy --config libs/ratanpy/pyproject.toml",
    ]

    for cmd in commands:
        if not run_command(cmd):
            success = False
            print(f"Failed: {cmd}")
        else:
            print(f"Passed: {cmd}")

    if success:
        print("Check passed")
        sys.exit(0)
    else:
        print("Finished with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()