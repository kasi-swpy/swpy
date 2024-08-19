import os, sys

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__))))

from api import kasi_mp

kasi_mp.download()