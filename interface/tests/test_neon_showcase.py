#!/usr/bin/env python3
"""Static smoke checks for the RetroVerse Neon Showcase page."""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import tempfile

PAGE = Path(__file__).resolve().parents[1] / "neon-showcase" / "index.html"
VIEWS = {"home", "library", "online", "friends", "multiplayer", "chat", "spectator", "themes", "settings"}

class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.views = set()
        self.targets = set()
        self.scripts = []
        self.inside_script = False
        self.duplicates = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        id_ = attrs.get("id")
        if id_:
            if id_ in self.ids:
                self.duplicates.add(id_)
            self.ids.add(id_)
        if tag == "section" and "view" in attrs.get("class", "").split():
            self.views.add(id_)
        for key in ("data-view", "data-open"):
            if key in attrs:
                self.targets.add(attrs[key])
        if tag == "script" and not attrs.get("src"):
            self.inside_script = True

    def handle_data(self, data):
        if self.inside_script:
            self.scripts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside_script = False

def main():
    page = PAGE.read_text(encoding="utf-8")
    parser = Structure()
    parser.feed(page)
    assert not parser.duplicates, f"Duplicate IDs: {parser.duplicates}"
    assert parser.views == VIEWS, f"View sections mismatch: {parser.views ^ VIEWS}"
    assert parser.targets <= parser.views, f"Broken view link: {parser.targets - parser.views}"
    for id_ in ("game-search", "room-search", "rooms", "chat-form", "chat-message", "chatlog", "themes-grid", "pad-status", "notice"):
        assert id_ in parser.ids, f"Missing interaction target: {id_}"
    assert len(parser.scripts) > 0, "Missing embedded interface JS"
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "showcase.js"
        script.write_text("\n".join(parser.scripts), encoding="utf-8")
        subprocess.run(["node", "--check", str(script)], check=True)
    print("Neon Showcase smoke checks passed: 9 views, navigation, IDs, JavaScript syntax")
    return 0

if __name__ == "__main__":
    sys.exit(main())
