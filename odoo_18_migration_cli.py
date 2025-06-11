#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
from pathlib import Path
from lxml import etree

NEW_ATTRS = ['invisible', 'required', 'readonly', 'column_invisible']

# ------------------- CLI ENTRY POINT -------------------
def main():
    parser = argparse.ArgumentParser(description="Outil de migration complet vers Odoo 18")
    parser.add_argument('directory', help="Chemin du dossier du module à migrer")
    parser.add_argument('--auto-replace', action='store_true', help="Remplacer automatiquement sans confirmation utilisateur")
    args = parser.parse_args()

    migrate_xml_structure(args.directory)
    migrate_attrs_states(args.directory, args.auto_replace)
    migrate_chatter_tags(args.directory)
    migrate_daterange_widget(args.directory)
    migrate_app_settings_blocks(args.directory)
    migrate_python_field_states(args.directory)

# ------------------- XML: TREE → LIST, view_mode -------------------
def migrate_xml_structure(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".xml"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                original = content
                content = re.sub(r"<tree(.*?)>", r"<list\1>", content)
                content = content.replace("</tree>", "</list>")
                content = re.sub(r'<field name="view_mode">([^<]*)</field>',
                                 lambda m: f'<field name="view_mode">{m.group(1).replace("tree", "list")}</field>',
                                 content)
                if content != original:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[STRUCTURE MODIFIÉE] {full_path}")

# ------------------- XML: ATTRS -------------------
def get_new_attrs(attrs):
    new_attrs = {}
    attrs = re.sub("&lt;", "<", attrs)
    attrs = re.sub("&gt;", ">", attrs)
    try:
        attrs_dict = eval(attrs.strip())
        for attr, attr_value in attrs_dict.items():
            if attr in NEW_ATTRS:
                expr = ' and '.join([f"{c[0]} {convert_op(c[1])} {quote_val(c[2])}" for c in attr_value])
                new_attrs[attr] = expr
    except Exception as e:
        print(f"[ERREUR ATTRS] {attrs} → {e}")
    return new_attrs

def convert_op(op):
    return {'=': '==', '!=': '!=', '>': '>', '<': '<', '>=': '>=', '<=': '<='}.get(op, op)

def quote_val(val):
    return f"'{val}'" if isinstance(val, str) else str(val)

def migrate_attrs_states(path, auto_replace):
    xml_files = [str(p) for p in Path(path).rglob('*.xml') if p.is_file()]
    for xml_file in xml_files:
        try:
            tree = etree.parse(xml_file)
            root = tree.getroot()
            modified = False
            for elem in root.xpath('//*[@attrs]'):
                attrs = elem.get('attrs')
                new_attrs = get_new_attrs(attrs)
                for key, value in new_attrs.items():
                    elem.set(key, value)
                if new_attrs:
                    del elem.attrib['attrs']
                    modified = True
            for elem in root.xpath('//*[@states]'):
                state_val = elem.get('states')
                if state_val:
                    elem.set('invisible', f"state != '{state_val}'")
                    del elem.attrib['states']
                    modified = True
            if modified:
                if auto_replace or input(f"Remplacer fichier modifié {xml_file} ? (y/N): ").lower().startswith('y'):
                    tree.write(xml_file, pretty_print=True, encoding='utf-8', xml_declaration=True)
                    print(f"[ATTRS/STATES MODIFIÉS] {xml_file}")
        except Exception as e:
            print(f"[ERREUR XML] {xml_file} → {e}")

# ------------------- XML: DATERANGE -------------------
def migrate_daterange_widget(path):
    for file in Path(path).rglob("*.xml"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        updated = re.sub(r"widget=\"daterange\" options=\"\{[^}]*related_start_date[^}]*\}\"",
                         r"widget=\"daterange\" options=\"{'end_date_field': 'end_date'}\"",
                         content)
        if updated != content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"[DATERANGE MODIFIÉ] {file}")

# ------------------- XML: CHATTER -------------------
def migrate_chatter_tags(path):
    for file in Path(path).rglob("*.xml"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        updated = re.sub(r"<div class=\"oe_chatter\">.*?</div>", "<chatter/>", content, flags=re.DOTALL)
        if updated != content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"[CHATTER MODIFIÉ] {file}")

# ------------------- XML: SETTINGS BLOCK -------------------
def migrate_app_settings_blocks(path):
    for file in Path(path).rglob("*.xml"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        updated = content
        updated = re.sub(r'<div class=\"app_settings_block[^>]*>', '<app>', updated)
        updated = re.sub(r'<h2>(.*?)</h2>', r'<block title="\1">', updated)
        updated = re.sub(r'<div class=\"row.*?o_settings_container\">\s*<label[^>]*for=\"(.*?)\".*?</div>', '', updated, flags=re.DOTALL)
        updated = re.sub(r'<div class=\"row.*?o_settings_container[^>]*>\s*<field[^>]*name=\"(.*?)\"[^>]*/>\s*</div>',
                         r'<setting string="\1"><field name="\1"/></setting>', updated)
        updated = re.sub(r'</div>', '</block>', updated)
        updated = re.sub(r'</div>', '</app>', updated)
        if updated != content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"[SETTINGS MODIFIÉ] {file}")

# ------------------- PYTHON: STATES SUPPRESSION -------------------
def migrate_python_field_states(path):
    for file in Path(path).rglob("*.py"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        updated = re.sub(r'states\s*=\s*\{[^}]*\},?', '', content)
        if updated != content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"[STATES FIELD SUPPRIMÉ] {file}")

if __name__ == "__main__":
    main()
