import pytest

from history import archive_snapshot


def test_snapshot_is_copied_with_timestamp(tmp_path):
    source = tmp_path / "meteora_data.json"
    source.write_text('[{"name": "A"}]')

    copy = archive_snapshot(source, tmp_path / "history")

    assert copy.parent.name == "history"
    assert copy.name.startswith("meteora_data_")
    assert copy.suffix == ".json"
    assert copy.read_text() == source.read_text()


def test_missing_source_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        archive_snapshot(tmp_path / "nope.json", tmp_path / "history")