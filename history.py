import shutil
from datetime import datetime
from pathlib import Path


def archive_snapshot(source, history_dir):
    """Copy the data file into history_dir with a timestamp in its name.

    Returns the path of the new copy. Raises FileNotFoundError if the
    source file does not exist.
    """
    source = Path(source)
    history_dir = Path(history_dir)
    history_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination = history_dir / f"{source.stem}_{stamp}{source.suffix}"
    shutil.copy2(source, destination)
    return destination