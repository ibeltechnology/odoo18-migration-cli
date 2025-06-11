import sys
import types
from pathlib import Path

# The main script depends on ``lxml`` which may not be available in the test
# environment. Create a lightweight mock so the module can be imported even if
# the dependency is missing.
lxml_mock = types.ModuleType("lxml")
lxml_mock.etree = types.ModuleType("lxml.etree")
sys.modules.setdefault("lxml", lxml_mock)
sys.modules.setdefault("lxml.etree", lxml_mock.etree)

# Ensure the repository root is on ``sys.path`` so the CLI module can be
# imported when tests are executed directly.
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from odoo_18_migration_cli import migrate_xml_structure


def test_tree_is_converted_to_list(tmp_path):
    xml_content = "<tree><field name='name'/></tree>"
    xml_file = tmp_path / "view.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    migrate_xml_structure(str(tmp_path))

    data = xml_file.read_text(encoding="utf-8")
    assert "<list" in data
    assert "</list>" in data
    assert "<tree" not in data
