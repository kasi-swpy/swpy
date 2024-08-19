import os, sys
import argparse

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__))))

from api import kasi_ecallisto

parser = argparse.ArgumentParser()
parser.add_argument("--uid", type=str)
args = parser.parse_args()

kasi_ecallisto.download(args.uid)