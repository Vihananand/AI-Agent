import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.agent import AgentSession
from agent.llm import tools
from agent.permissions import tool_requires_approval
from agent.tools import (
    TOOL_REGISTRY,
    calculate,
    get_file_hash,
    list_open_ports,
    search_files,
    search_text,
)


def main():
    session = AgentSession(max_context_chars=2000)
    session.add_user_message("old question")
    session.messages.append({"role": "assistant", "content": "old answer " * 100})
    session.add_user_message("new question")
    assert "old question" not in str(session.messages)
    assert "new question" in str(session.messages)

    assert calculate("2 + 3 * 4") == "14"
    assert calculate("__import__('os').getcwd()").startswith("Error:")
    assert list_open_ports(0, 10).startswith("Error:")
    assert "127.0.0.1" in list_open_ports(1, 1)
    assert tool_requires_approval("list_open_ports")
    assert not tool_requires_approval("check_port")

    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "target.txt"
        target.write_text("target", encoding="utf-8")
        assert str(target) in search_files(directory, "target.txt", max_depth=0)
        assert search_files(directory, "target.txt", max_depth=-1).startswith("Error:")

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as file:
        file.write("First line\nFind this line\n")
        file_path = file.name

    try:
        assert "2: Find this line" in search_text(file_path, "find this line")
        expected_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
        assert get_file_hash(file_path) == f"sha256: {expected_hash}"
    finally:
        Path(file_path).unlink(missing_ok=True)

    schema_names = {tool["function"]["name"] for tool in tools}
    assert schema_names == set(TOOL_REGISTRY)
    print(f"Passed tool checks for {len(TOOL_REGISTRY)} tools.")


if __name__ == "__main__":
    main()