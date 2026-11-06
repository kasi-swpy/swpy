# swpy

Python package and command-line tool for fetching KASI space-weather data from the SWPy
distribution server (distribution API).

- **File datasets**: observation images and original files (SDO, SOHO/LASCO, GOES, NOAA SWPC,
  OMNI, etc.). List them, then download.
- **Table datasets**: measurements stored as values in the database (realtime solar wind, GOES
  X-ray and proton, Kp, Dst, etc.). Download them as CSV.

The server tells you which datasets exist (`swpy datasets`). A dataset added on the server shows
up immediately, with no change to this package.

## Install

```bash
pip install git+https://github.com/kasi-swpy/swpy
```

Python 3.10 or later; the only dependency is `requests`.

## Configuration

| Variable | Meaning |
|---|---|
| `SWPY_SERVER` | Distribution server URL (e.g. `http://<server>:8032`) — required |
| `SWPY_MODE` | `api` (default) or `direct` |
| `SWPY_STORAGE_ROOT` | In `direct` mode, where the SWPy storage is mounted (the directory holding `swds/`) |

On the command line use `--server`, `--mode`, `--storage-root` instead; in Python, pass them as
`Client(...)` arguments.

### The two modes

- **`api`**: for hosts that cannot see the storage (e.g. external servers). Files are downloaded
  from the server — a single file as is, several as zip archives that are unpacked automatically
  into the same directory tree as the storage (below `swds/data/`).
- **`direct`**: for internal servers that mount the storage (NAS) the same way. Nothing is
  transferred; the paths from the server's listing are mapped onto the local storage root and
  returned (each file is checked to exist).

Table datasets (CSV) work the same way in both modes.

## Command line

```bash
swpy datasets                     # file and table datasets (--files / --tables)
swpy list nasa_soho_c2 --start 2026-10-17T00:00 --end 2026-10-17T06:00
swpy get  nasa_soho_c2 --start 2026-10-17T00:00 --end 2026-10-17T06:00 -o data/
swpy table rt_kp                  # columns, time column, time range, row count
swpy csv  rt_kp --start 2026-10-17 --end 2026-10-18 --columns datetime,estimated_kp
```

Times are ISO-8601, UTC. `--start` is inclusive, `--end` exclusive.

## Python

```python
from swpy import Client

c = Client(server="http://<server>:8032")           # mode="direct", storage_root=... also possible
c.datasets()                                          # {"files": [...], "tables": [...]}
files = c.files("nasa_soho_c2", "2026-10-17", "2026-10-18")
paths = c.get("nasa_soho_c2", "2026-10-17", "2026-10-18", dest="data")
csv_path = c.csv("rt_goes_xray", "2026-10-17", "2026-10-18", columns=["datetime", "flux_long"])
```

## Facts for summaries

```python
c.summary("2026-10-27", "2026-11-03")       # daily extremes, G/R/S levels, events, data coverage
c.summary("2024-05-08", "2024-05-16", source="definitive")   # past years: definitive data
c.events("2026-10-10", "2026-10-12", types="storm,flare", min_class="C1")
c.texts("2026-11-02", "2026-11-03", kinds="rsga,forecast")   # issued NOAA SWPC prose
c.table_json("df_omni_hourly", "2025-01-01", "2026-01-01",
             columns=["datetime", "kp_x10", "dst"], resample="day", agg="max")
c.headers("aia.lev1_euv_12s", "2024-05-10T16:00", "2024-05-10T19:00",   # SDO FITS header catalogue
          wavelength=193, good_only=True, keys=["DATAMEDN"])
```

The server returns facts only (numbers, NOAA scale levels, event lists and how
much of each day the data cover); writing a summary is up to you or your AI
assistant. Missing data is reported as such, never as a quiet day.

## Use with an AI assistant (MCP)

`swpy-mcp` is an [MCP](https://modelcontextprotocol.io) server exposing the facts
as tools (`get_period_summary`, `list_events`, `get_issued_texts`,
`get_timeseries`, `find_observations`, `list_datasets`), so an assistant such as Claude can answer
"summarize last week's space weather" from the data.

```bash
pip install "swpy[mcp] @ git+https://github.com/kasi-swpy/swpy"
```

Claude Code:

```bash
claude mcp add swpy --env SWPY_SERVER=http://<server>:8032 -- swpy-mcp
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "swpy": {
      "command": "swpy-mcp",
      "env": {"SWPY_SERVER": "http://<server>:8032"}
    }
  }
}
```

Use the full path to `swpy-mcp` if it is not on the PATH Claude Desktop sees.

## Limits

- The server packs at most 5,000 files / 20 GB into one zip. The client splits requests into
  batches of 1,000 files / 5 GB, so large requests can be used as is.
- There is no authentication.
