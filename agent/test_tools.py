import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.llm import tools
from agent.tools import TOOL_REGISTRY, calculate, get_file_hash, search_text


def main():
    assert calculate("2 + 3 * 4") == "14"
    assert calculate("__import__('os').getcwd()").startswith("Error:")

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