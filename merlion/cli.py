"""Console script for merlion."""
import argparse
import sys

from merlion import Merlion


def main():
    """Console script for merlion."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    # print("Arguments: " + str(args._))
    # print("Replace this message by putting your code into "
    #       "merlion.cli.main")

    merlion = Merlion()
    merlion.load('merlion.py')
    merlion.map()
    merlion.output()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
