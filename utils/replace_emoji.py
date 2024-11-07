from pathlib import Path
import emoji


for file in Path('.').rglob('*.md'):
    with file.open() as f:
        content = f.read()
    with file.open('w') as f:
        f.write(emoji.emojize(content))