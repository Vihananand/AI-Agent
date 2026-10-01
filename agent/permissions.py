import shlex

from agent.logging_config import get_logger

logger = get_logger("permissions")
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
APPROVAL_TOOLS = {"list_open_ports"}


def tool_requires_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_TOOLS


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
        logger.info("Command classified; classification=DENY reason=empty_or_invalid")
        return "DENY"
    # Normalize Windows executable names
    executable = executable.lower()

    if executable.endswith(".exe"):
        executable = executable[:-4]
    # Explicitly dangerous commands
    if executable in DENIED_COMMANDS:
        logger.info("Command classified; classification=DENY executable=%s", executable)
        return "DENY"
    # Allowed commands
    if executable in ALLOWED_COMMANDS:

        if not arguments:
            if not ALLOWED_COMMANDS[executable]:
                logger.info("Command classified; classification=ALLOW executable=%s", executable)
                return "ALLOW"
        first_argument = arguments[0]

        if first_argument in ALLOWED_COMMANDS[executable]:
            logger.info("Command classified; classification=ALLOW executable=%s", executable)
            return "ALLOW"
    # Commands requiring approval
    if executable in APPROVAL_COMMANDS:

        if not arguments:
            logger.info("Command classified; classification=DENY executable=%s", executable)
            return "DENY"
        first_argument = arguments[0]

        if first_argument in APPROVAL_COMMANDS[executable]:
            logger.info("Command classified; classification=APPROVAL executable=%s", executable)
            return "APPROVAL"
    logger.info("Command classified; classification=DENY executable=%s", executable)
    return "DENY"

def request_approval() -> bool:

    # Ask the user for explicit permission to execute a command.

    print("\n⚠️  APPROVAL REQUIRED")
    response = input("Allow this command? (yes/no): ")
    approved = response.strip().lower() in {
        "yes",
        "y",
    }
    logger.info("Approval prompt completed; approved=%s", approved)
    return approved