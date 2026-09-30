import shlex
ALLOWED_COMMANDS = {
    "python": {
        "--version",
    },
    "git": {
        "status",
        "branch",
        "log",
        "diff",
    },
    "pip": {
        "list",
    },
    "dir": set(),
    "ls": set(),
}
APPROVAL_COMMANDS = {
    "git": {
        "commit",
        "checkout",
        "switch",
        "merge",
    },
    "pip": {
        "install",
        "uninstall",
    },
    "python": {
        "script",
    },
}
DENIED_COMMANDS = {
    "rm",
    "rmdir",
    "del",
    "format",
    "shutdown",
    "reboot",
}
def parse_command(command: str):
    # Parse a shell command into executable and arguments.

    try:
        parts = shlex.split(command)

        if not parts:
            return None, []

        executable = parts[0]
        arguments = parts[1:]

        return executable, arguments

    except ValueError:
        return None, []
def classify_command(command: str) -> str:
    # Return the risk level of a command.
    # Possible results: ALLOW, APPROVAL, or DENY.

    executable, arguments = parse_command(command)

    if executable is None:
        return "DENY"
    # Normalize Windows executable names
    executable = executable.lower()

    if executable.endswith(".exe"):
        executable = executable[:-4]
    # Explicitly dangerous commands
    if executable in DENIED_COMMANDS:
        return "DENY"
    # Allowed commands
    if executable in ALLOWED_COMMANDS:

        if not arguments:
            if not ALLOWED_COMMANDS[executable]:
                return "ALLOW"
        first_argument = arguments[0]

        if first_argument in ALLOWED_COMMANDS[executable]:
            return "ALLOW"
    # Commands requiring approval
    if executable in APPROVAL_COMMANDS:

        if not arguments:
            return "DENY"
        first_argument = arguments[0]

        if first_argument in APPROVAL_COMMANDS[executable]:
            return "APPROVAL"
    return "DENY"

def request_approval(command: str) -> bool:

    # Ask the user for explicit permission to execute a command.

    print("\n⚠️  APPROVAL REQUIRED")
    print(f"Command: {command}")
    response = input("Allow this command? (yes/no): ")
    return response.strip().lower() in {
        "yes",
        "y",
    }