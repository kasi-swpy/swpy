import os, sys
import argparse

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__))))

from api import kasi_mm

parser = argparse.ArgumentParser()
parser.add_argument("--uid", type=str)
args = parser.parse_args()

kasi_mm.download(args.uid)