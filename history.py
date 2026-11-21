import shutil
from datetime import datetime, timezone
from pathlib import Path


def archive_snapshot(source, history_dir):
    """It copies the data file into history_dir with a timestamp in its name.
    """
    source = Path(source)
    history_dir = Path(history_dir)
    history_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    destination = history_dir / f"{source.stem}_{stamp}{source.suffix}"
    shutil.copy2(source, destination)
    return destination