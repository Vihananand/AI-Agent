import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.permissions import classify_command
commands = [
    "git status",
    "git branch",
    "git log",
    "git diff",
    "pip list",
    "python --version",
    "dir",
    "ls",
    "git commit",
    "git checkout",
    "pip install requests",

    "rm -rf .",
    "del /s /q *",
    "format C:",
]
for command in commands:
    result = classify_command(command)
    print(f"{command:<25} -> {result}")