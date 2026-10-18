# swpy

KASI 우주기상 자료를 SWPy 배포 서버(distribution API)에서 받아 쓰는 Python 패키지와 명령행 도구.

- **파일 자료**: 관측 영상·원본 파일(SDO, SOHO/LASCO, GOES, NOAA SWPC, OMNI 등). 목록을 보고 받는다.
- **표 자료**: DB에 값으로 들어 있는 측정값(실시간 태양풍, GOES X선·양성자, Kp, Dst 등). CSV로 받는다.

자료 종류는 서버가 알려준다(`swpy datasets`). 새 자료가 서버에 추가되면 패키지 수정 없이 바로 보인다.

## 설치

```bash
pip install git+https://github.com/kasi-swpy/swpy
```

Python 3.10 이상, 의존성은 `requests` 하나.

## 설정

| 변수 | 뜻 |
|---|---|
| `SWPY_SERVER` | 배포 서버 주소 (예: `http://<server>:8032`) — 필수 |
| `SWPY_MODE` | `api`(기본) 또는 `direct` |
| `SWPY_STORAGE_ROOT` | `direct` 모드에서 SWPy 저장소가 마운트된 위치(`swds/`를 담은 디렉터리) |

명령행에서는 `--server`, `--mode`, `--storage-root`로, Python에서는 `Client(...)` 인자로 대신할 수 있다.

### 두 모드

- **`api`**: 저장소가 보이지 않는 곳(외부 서버 등). 파일을 서버에서 내려받는다. 파일 1개는 그대로, 여러 개는 zip으로 받아 자동으로 풀며, 저장소와 같은 디렉터리 구조(`swds/data/` 아래)로 놓인다.
- **`direct`**: 저장소(NAS)가 같은 방식으로 마운트된 내부망 서버. 아무것도 전송하지 않고, 서버 목록의 경로를 로컬 저장소 경로로 바꿔 돌려준다(파일이 실제로 있는지 확인).

표 자료(CSV)는 두 모드에서 똑같이 동작한다.

## 명령행

```bash
swpy datasets                     # 파일·표 자료 목록 (--files / --tables)
swpy list nasa_soho_c2 --start 2026-10-17T00:00 --end 2026-10-17T06:00
swpy get  nasa_soho_c2 --start 2026-10-17T00:00 --end 2026-10-17T06:00 -o data/
swpy table rt_kp                  # 열, 시간 열, 기간, 행 수
swpy csv  rt_kp --start 2026-10-17 --end 2026-10-18 --columns datetime,estimated_kp
```

시간은 ISO-8601, UTC 기준. `--start`는 포함, `--end`는 제외.

## Python

```python
from swpy import Client

c = Client(server="http://<server>:8032")           # mode="direct", storage_root=... 도 가능
c.datasets()                                          # {"files": [...], "tables": [...]}
files = c.files("nasa_soho_c2", "2026-10-17", "2026-10-18")
paths = c.get("nasa_soho_c2", "2026-10-17", "2026-10-18", dest="data")
csv_path = c.csv("rt_goes_xray", "2026-10-17", "2026-10-18", columns=["datetime", "flux_long"])
```

## 제한

- 서버는 zip 하나에 최대 5,000개·20 GB까지 묶는다. 클라이언트는 1,000개·5 GB 단위로 나눠 요청하므로 큰 요청도 그대로 쓰면 된다.
- 인증은 없다.
