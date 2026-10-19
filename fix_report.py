import re

with open("generate_report.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "try:" in line and "doc.add_picture(" in lines[lines.index(line)+1]:
        skip = True
    elif "except:" in line and skip:
        continue
    elif "add_body(doc, \"[Missing" in line and skip:
        skip = False
        continue

# Wait, this is error prone. Let's just restore the original from github or git if possible.
