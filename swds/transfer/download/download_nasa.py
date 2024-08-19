import os, sys
import argparse

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__))))

from api import nasa

parser = argparse.ArgumentParser()
parser.add_argument("--uid", type=str)
args = parser.parse_args()

nasa.download(args.uid)