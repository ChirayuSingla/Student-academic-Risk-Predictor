"""Extract only known dataset files from a local UCI archive (including nested ZIP)."""
import argparse
import io
import zipfile
from pathlib import Path
from urllib.request import urlopen

from .config import ROOT
from .utils import sha256, write_json

SOURCE = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
FILES = ("student-mat.csv", "student-por.csv", "student.txt", "student-merge.R")


def dataset_members(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if "student-mat.csv" in archive.namelist():
            missing = set(FILES) - set(archive.namelist())
            if missing:
                raise ValueError(f"UCI archive is incomplete; missing files: {sorted(missing)}")
            return {name: archive.read(name) for name in FILES}
        if "student.zip" in archive.namelist():
            return dataset_members(archive.read("student.zip"))
    raise ValueError("Archive does not contain the original UCI student-mat.csv.")


def acquire(archive_path, verify_official=False):
    archive_path = Path(archive_path).resolve()
    members = dataset_members(archive_path.read_bytes())
    verified = False
    if verify_official:
        with urlopen(SOURCE, timeout=60) as response:
            official = dataset_members(response.read())
        for name in FILES:
            if members.get(name) != official.get(name):
                raise ValueError(f"Local and official UCI contents differ: {name}")
        verified = True
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    for name, payload in members.items():
        (data_dir / name).write_bytes(payload)
    provenance = {
        "source_url": SOURCE, "dataset_doi": "10.24432/C5TG7T",
        "citation": "Cortez, P. (2008). Student Performance [Dataset]. UCI Machine Learning Repository.",
        "license": "CC BY 4.0", "local_archive": archive_path.name,
        "archive_sha256": sha256(archive_path), "official_contents_verified": verified,
        "files": {name: {"sha256": sha256(data_dir / name), "bytes": (data_dir / name).stat().st_size}
                  for name in members},
        "experiment_file": "student-mat.csv", "synthetic_data": False,
    }
    write_json(data_dir / "provenance.json", provenance)
    print(f"Extracted {list(members)}; official bytes verified={verified}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "student+performance.zip")
    parser.add_argument("--verify-official", action="store_true")
    args = parser.parse_args()
    acquire(args.archive, args.verify_official)


if __name__ == "__main__":
    main()
