"""Restore byte-identical approved PNGs from connector-friendly text chunks."""
import base64
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def unpack():
    target = BASE/'assets'
    target.mkdir(exist_ok=True)
    for entry in json.loads((BASE/'artwork/manifest.json').read_text()):
        path = target/entry['file']
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']:
            continue
        data = base64.b64decode(''.join((BASE/'artwork'/part).read_text() for part in entry['parts']), validate=True)
        if len(data) != entry['size_bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError(f"Approved artwork checksum mismatch: {entry['file']}")
        path.write_bytes(data)
    return target

if __name__ == '__main__':
    print(unpack())
