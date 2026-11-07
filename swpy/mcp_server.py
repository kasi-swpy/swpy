"""MCP server: SWPy space-weather data as tools for AI assistants.

Run by an MCP client (Claude Desktop, Claude Code, ...) over stdio:

    swpy-mcp                      # needs SWPY_SERVER (the distribution API URL)

The tools return facts from the SWPy distribution API — numbers, NOAA scale
levels, event lists, data coverage and the issued SWPC texts. Writing the
summary is the assistant's job; the instructions below tell it how to stay
faithful to the facts.

Requires the optional dependency: pip install "swpy[mcp]".
"""

import requests
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from swpy.client import Client

INSTRUCTIONS = """\
SWPy serves KASI's space-weather database. Use these tools to answer questions
about space weather (geomagnetic storms, solar flares, CMEs, solar wind,
energetic particles) for a time window.

- Start with get_period_summary for any "what happened" or "summarize" question:
  one call returns daily extremes, the NOAA G/R/S levels reached, events and
  data coverage. Use list_events, get_issued_texts and get_timeseries for detail,
  and find_observations for solar images (SDO, SOHO LASCO coronagraph and MDI,
  STEREO SECCHI coronagraphs/heliospheric imagers, Solar Orbiter PHI: frames,
  quality, pointing) of a time.
- All times are UTC. Windows are [start, end); a bare date means 00:00 UTC.
- source="auto" (default) uses realtime data and fills gaps with definitive
  data. For past years use source="definitive" (GOES since 2017, OMNI since
  1995): realtime data start in October 2026, and definitive data lag real
  time by days to months. Each coverage entry names the table it came from.
- Report numbers as the tools give them, with units, and say which day or time
  they occurred. Use NOAA scale names (G1-G5, R1-R5, S1-S5) as returned.
- Check coverage and notes before concluding anything is quiet: a fraction of 0
  or a note means NO DATA, not no activity — say so explicitly.
- Quote SWPC wording (get_issued_texts) when it adds the forecasters' view, and
  attribute it to NOAA SWPC.
"""

server = MCPServer(name="swpy", title="SWPy space weather", instructions=INSTRUCTIONS)
_client = None


def _api():
    """The shared distribution-API client (SWPY_SERVER from the environment)."""
    global _client
    if _client is None:
        _client = Client()
    return _client


def _call(fn, *args, **kwargs):
    """Call the API; raise HTTP failures as readable tool errors.

    ToolError (rather than an error payload) makes the MCP client mark the
    call as failed with this message, so the assistant reads the reason and
    cannot mistake it for data.
    """
    try:
        return fn(*args, **kwargs)
    except requests.HTTPError as exc:
        try:
            detail = exc.response.json().get("detail")
        except ValueError:
            detail = exc.response.text
        raise ToolError(f"server error {exc.response.status_code}: {detail}") from None
    except requests.ConnectionError as exc:
        raise ToolError(f"cannot reach the SWPy server: {exc}") from None


@server.tool()
def get_period_summary(start: str | None = None, end: str | None = None,
                       min_flare_class: str = "M1.0", source: str = "auto") -> dict:
    """Space-weather facts for a UTC window [start, end); default the last 7 days.

    Returns daily extremes (Kp, Dst, X-ray flux and flare class, >=10 MeV
    protons, >=2 MeV electrons, solar wind speed/density, IMF Bz), the NOAA
    G/R/S levels reached, events (flares >= min_flare_class, storms, CMEs,
    SWPC alerts), per-day data coverage and notes on missing data.

    Args:
        start: ISO date or time (UTC), e.g. "2026-10-27".
        end: ISO date or time (UTC), exclusive.
        min_flare_class: Smallest flare class to list, e.g. "C5", "M1".
        source: "auto", "realtime" or "definitive" (see the instructions).
    """
    return _call(_api().summary, start, end, min_flare_class, source)


@server.tool()
def list_events(start: str | None = None, end: str | None = None,
                types: str = "flare,storm,cme,alert", min_flare_class: str = "M1.0",
                source: str = "auto") -> dict:
    """Event lists for a UTC window: flares (by peak time), geomagnetic storms
    (3-hour Kp >= 5), CMEs (DONKI; CACTus halo detections) and SWPC alert
    headlines. types is a comma-separated subset of flare,storm,cme,alert.
    source picks the Kp grade of the storm list ("definitive" for past years).
    Flares: the realtime SWPC list from October 2026, the NCEI GOES-R flare
    summary from 2017 (source="definitive" for past years)."""
    return _call(_api().events, start, end, types, min_flare_class, source)


@server.tool()
def get_issued_texts(start: str | None = None, end: str | None = None,
                     kinds: str = "forecast,rsga,alert", limit: int = 10) -> dict:
    """NOAA SWPC prose issued in the window, newest first: 3-day forecasts
    (forecast), daily Reports of Solar-Geophysical Activity (rsga) and alert/
    warning messages (alert). kinds is a comma-separated subset."""
    return _call(_api().texts, start, end, kinds, limit)


@server.tool()
def get_timeseries(table: str, start: str | None = None, end: str | None = None,
                   columns: str | None = None, resample: str | None = None,
                   agg: str = "mean", limit: int = 2000) -> dict:
    """Rows of one measurement table for a UTC window, as columns + row arrays.

    Prefer resample="hour" or "day" (with agg "mean", "min" or "max") for
    windows longer than a few hours: raw tables hold 1-minute rows. Rows are
    grouped per satellite/energy/source. Use list_datasets for table names
    (e.g. rt_kp, rt_rtsw_wind, rt_goes_xray, df_omni_hourly).

    Args:
        columns: Comma-separated column subset (default: all).
        limit: Maximum rows returned (truncated is true when cut).
    """
    cols = [c.strip() for c in columns.split(",")] if columns else None
    return _call(_api().table_json, table, start, end, cols, resample, agg, limit)


@server.tool()
def find_observations(series: str = "aia.lev1_euv_12s", start: str | None = None,
                      end: str | None = None, wavelength: float | None = None,
                      detector: str | None = None, observatory: str | None = None,
                      good_only: bool = True,
                      keys: str | None = None, limit: int = 200) -> dict:
    """Solar image FITS observations (header catalogue) in a UTC window.

    Series: aia.lev1_euv_12s (SDO AIA EUV; wavelength 94, 131, 171, 193, 211,
    304, 335), hmi.m_45s / hmi.m_720s (SDO magnetograms), hmi.ic_45s (SDO
    continuum) — about one frame per hour per channel for most years;
    mdi.fd_m_96m_lev182 (SOHO MDI magnetograms, 1996-2011); lasco.lev05 (SOHO
    LASCO coronagraph level 0.5, 1995-; detector C2 or C3 — use it for CMEs);
    secchi.lev05 (STEREO SECCHI level 0.5, 2006-; observatory STEREO_A or
    STEREO_B (B ends 2014), detector COR1, COR2, HI1 or HI2 — CMEs seen from
    off the Sun-Earth line, see hgln_obs; downlink SW is the low-resolution
    space-weather beacon); phi.l2 (Solar Orbiter PHI magnetograms; the
    spacecraft is not on the Sun-Earth line: see dsun_au, hgln_obs). Each row
    has observation times, quality (good_only keeps good frames: SDO QUALITY
    = 0, LASCO/SECCHI no missing blocks; MDI and PHI have no condition),
    exposure, WCS basics and the file
    path (relative to the archive root holding solar_images/; files are not
    downloadable through this API). keys adds header keywords (comma-separated,
    FITS names with '-' as '__', e.g. DATAMEDN).
    """
    extra = [k.strip() for k in keys.split(",")] if keys else None
    return _call(_api().headers, series, start, end, wavelength=wavelength,
                 detector=detector, observatory=observatory, good_only=good_only,
                 keys=extra, limit=limit)


@server.tool()
def list_datasets() -> dict:
    """Measurement tables (with their time column and columns) and file
    datasets (images and files by data_id) that SWPy serves."""
    found = _call(_api().datasets)
    return {"tables": found["tables"],
            "file_datasets": [d["data_id"] for d in found["files"]]}


def main():
    """Entry point of the swpy-mcp command (stdio transport)."""
    server.run("stdio")


if __name__ == "__main__":
    main()
