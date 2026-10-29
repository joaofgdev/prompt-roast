"""Criação do executável local autocontido."""
from pathlib import Path
import os
import shutil
import tempfile
import sys
import zipfile
import zipapp


def build_runtime(destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(sys.argv[0]):
        source = Path(sys.argv[0]).resolve()
        if source != destination.resolve():
            shutil.copyfile(source, destination)
        return destination
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        package = Path(__file__).parent
        shutil.copytree(package, root / "prompt_roast", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (root / "__main__.py").write_text("from prompt_roast.cli import main\nmain()\n", encoding="utf-8")
        fd, name = tempfile.mkstemp(dir=destination.parent, prefix=".prompt-roast-")
        os.close(fd)
        try:
            zipapp.create_archive(root, name, interpreter="/usr/bin/env python3")
            os.replace(name, destination)
        finally:
            if os.path.exists(name):
                os.unlink(name)
    return destination
