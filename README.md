# 🛠️ Odoo 18 Migration CLI

CLI tool to automate the migration of Odoo 17 modules to version 18.0. This script converts outdated XML and Python syntax to the latest Odoo 18 standards.

## ✅ Supported Features

### XML

- ✅ Replace `<tree>` with `<list>`
- ✅ Change `view_mode="tree,form"` to `list,form`
- ✅ Convert `attrs` to Odoo 18 native attributes (`invisible`, `readonly`, etc.)
- ✅ Transform `states="draft"` into `invisible="state != 'draft'"`
- ✅ Simplify chatter blocks: `<div class="oe_chatter">` → `<chatter/>`
- ✅ Update `daterange` widget options
- ✅ Reformat `res.config.settings` views to use `<app>`, `<block>`, and `<setting>`

### Python

- ✅ Remove `states={...}` from field definitions

---

## 📦 Installation

No installation required. Run the script using Python 3:

```bash
python3 odoo_18_migration_cli.py /path/to/your/module --auto-replace
```

### ⚙️ Options

- `--auto-replace` : apply changes without confirmation per file.

---

## 📁 Repository Structure

```
odoo18-migration-cli/
├── odoo_18_migration_cli.py       # Main script
├── README.md                     # Instructions
├── LICENSE                       # MIT License
├── examples/                     # Before/after samples (optional)
└── docs/
    └── guide_migration_odoo18.md  # Detailed migration guide
```

---

## 📄 License

Distributed under the MIT License.

---

## 🙌 Contributions

Contributions are welcome via pull request!

Report bugs or suggest features via [Issues](https://github.com/your-user/odoo18-migration-cli/issues)

---

## 📘 Reference: Odoo 18 Migration Guide

See docs/guide\_migration\_odoo18.md for a full summary of syntax updates in Odoo 18.

