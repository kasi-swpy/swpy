"""Client for the SWPy data distribution API.

Two modes share one listing (the server's catalog):

- "api" (default): files are downloaded from the server — one file as is,
  several as zip archives that are unpacked into the destination, keeping
  the archive's directory tree.
- "direct": for hosts that mount the SWPy storage themselves. Nothing is
  transferred; each listed logical path is resolved under the local
  storage root (SWPY_STORAGE_ROOT) and checked to exist.

Table (measurement) datasets are exported as CSV in both modes.
"""

import os
import tempfile
import zipfile
from pathlib import Path

import requests

PAGE = 10000                     # files per listing request (server maximum)
BATCH_FILES = 1000               # files per zip request
BATCH_BYTES = 5 * 10**9          # bytes per zip request
CHUNK = 1 << 20
DATA_PREFIX = "swds/data/"       # logical-path prefix the archives drop


def _check(response):
    """Raise requests.HTTPError for an error status, body read first so the
    server's detail survives the closing of a streamed response."""
    if not response.ok:
        response.content
    response.raise_for_status()


def _iso(value):
    """Format a datetime (or pass an ISO string) for a query parameter."""
    if value is None or isinstance(value, str):
        return value
    return value.isoformat()


class Client:
    """Access SWPy datasets through the distribution API.

    Args:
        server: Base URL of the distribution server, e.g.
            "http://host:8032". Defaults to the SWPY_SERVER variable.
        mode: "api" or "direct". Defaults to SWPY_MODE, else "api".
        storage_root: Local storage root for direct mode (the directory
            holding swds/). Defaults to SWPY_STORAGE_ROOT.
        timeout: Seconds to wait for the server to respond.

    Raises:
        ValueError: If the server URL is missing, the mode is unknown, or
            direct mode has no storage root.
    """

    def __init__(self, server=None, mode=None, storage_root=None, timeout=60):
        self.server = (server or os.environ.get("SWPY_SERVER") or "").rstrip("/")
        if not self.server:
            raise ValueError("no server: pass server= or set SWPY_SERVER")
        self.mode = mode or os.environ.get("SWPY_MODE") or "api"
        if self.mode not in ("api", "direct"):
            raise ValueError(f"unknown mode: {self.mode} (api or direct)")
        root = storage_root or os.environ.get("SWPY_STORAGE_ROOT")
        self.storage_root = Path(root).expanduser() if root else None
        if self.mode == "direct" and self.storage_root is None:
            raise ValueError("direct mode needs storage_root= or SWPY_STORAGE_ROOT")
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path):
        return f"{self.server}/api/v1/{path}"

    def _get(self, path, **params):
        """GET a JSON endpoint; raises requests.HTTPError on failure."""
        response = self.session.get(self._url(path), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    # ---- discovery -----------------------------------------------------------

    def datasets(self):
        """All datasets: {"files": [...], "tables": [...]}."""
        return self._get("datasets")

    def table_info(self, table):
        """A table's columns, time column, row count and time range."""
        return self._get(f"tables/{table}")

    def files(self, data_id, start=None, end=None):
        """List a file dataset's files in [start, end), oldest first.

        Args:
            data_id: File dataset id (see datasets()).
            start: Inclusive start (datetime or ISO string; naive = UTC).
            end: Exclusive end.

        Returns:
            List of {"path", "storage_id", "name", "time", "size"} dicts;
            path is the logical archive path. In direct mode each entry
            also carries "local", its path under the storage root.
        """
        entries, offset = [], 0
        while True:
            page = self._get(f"files/{data_id}", start=_iso(start), end=_iso(end),
                             limit=PAGE, offset=offset)
            entries += page["files"]
            offset += len(page["files"])
            if not page["files"] or offset >= page["total"]:
                break
        if self.mode == "direct":
            for entry in entries:
                entry["local"] = str(self.storage_root / entry["path"])
        return entries

    # ---- files -----------------------------------------------------------------

    def get(self, data_id, start=None, end=None, dest="."):
        """Fetch a file dataset's files in [start, end).

        api mode downloads into dest, keeping the archive tree below
        swds/data/ (e.g. dest/nasa/soho/c2/2026/20261017/...). direct mode
        transfers nothing and returns the files' local paths.

        Returns:
            List of Paths of the fetched (or, in direct mode, located) files.

        Raises:
            FileNotFoundError: In direct mode, when listed files are missing
                under the storage root (wrong root, or storage not mounted).
        """
        entries = self.files(data_id, start, end)
        if self.mode == "direct":
            paths = [Path(e["local"]) for e in entries]
            missing = [p for p in paths if not p.is_file()]
            if missing:
                raise FileNotFoundError(
                    f"{len(missing)} of {len(paths)} files not under {self.storage_root} "
                    f"(first: {missing[0]})")
            return paths
        return self.download([e["path"] for e in entries], dest,
                             sizes=[e["size"] or 0 for e in entries])

    def download(self, paths, dest=".", sizes=None):
        """Download logical paths into dest (api mode transfer).

        One file is fetched as is; several go through zip archives of at
        most BATCH_FILES files / BATCH_BYTES bytes each, unpacked on arrival.

        Returns:
            List of Paths of the downloaded files.
        """
        dest = Path(dest)
        if not paths:
            return []
        if len(paths) == 1:
            target = dest / paths[0].removeprefix(DATA_PREFIX)
            target.parent.mkdir(parents=True, exist_ok=True)
            with self.session.get(self._url("download"), params={"path": paths[0]},
                                  stream=True, timeout=self.timeout) as response:
                _check(response)
                self._save(response, target)
            return [target]
        sizes = sizes or [0] * len(paths)
        out, batch, batch_bytes = [], [], 0
        for path, size in zip(paths, sizes):
            if batch and (len(batch) >= BATCH_FILES or batch_bytes + size > BATCH_BYTES):
                out += self._fetch_zip(batch, dest)
                batch, batch_bytes = [], 0
            batch.append(path)
            batch_bytes += size
        out += self._fetch_zip(batch, dest)
        return out

    def _save(self, response, target):
        """Stream a response body into target via a temporary file."""
        part = target.with_name(target.name + ".part")
        with open(part, "wb") as fh:
            for block in response.iter_content(CHUNK):
                fh.write(block)
        part.replace(target)

    def _fetch_zip(self, paths, dest):
        """Fetch one zip of paths and unpack it into dest."""
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "batch.zip"
            with self.session.post(self._url("archive"), json={"paths": paths},
                                   stream=True, timeout=self.timeout) as response:
                _check(response)
                self._save(response, archive)
            with zipfile.ZipFile(archive) as zf:
                names = zf.namelist()
                for name in names:
                    # Archive names come from server-side logical paths;
                    # refuse anything that would land outside dest.
                    if Path(name).is_absolute() or ".." in Path(name).parts:
                        raise ValueError(f"unsafe archive member: {name}")
                zf.extractall(dest)
        return [dest / name for name in names]

    # ---- tables ----------------------------------------------------------------

    def csv(self, table, start=None, end=None, columns=None, dest=None):
        """Export a table's rows in [start, end) as a CSV file.

        Args:
            table: Table name (see datasets()).
            start: Inclusive start on the table's time column.
            end: Exclusive end.
            columns: Optional list of column names (default: all).
            dest: Output file path; default "<table>_<start>_<end>.csv" in
                the current directory.

        Returns:
            Path of the written CSV.
        """
        if dest is None:
            span = "_".join(_iso(t)[:10].replace("-", "") for t in (start, end) if t)
            dest = f"{table}_{span}.csv" if span else f"{table}.csv"
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        params = {"start": _iso(start), "end": _iso(end),
                  "columns": ",".join(columns) if columns else None}
        with self.session.get(self._url(f"tables/{table}/csv"), params=params,
                              stream=True, timeout=self.timeout) as response:
            _check(response)
            self._save(response, dest)
        return dest
