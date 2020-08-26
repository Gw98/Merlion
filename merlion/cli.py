"""Console script for merlion."""
import argparse
import sys

from merlion import Merlion


from parser import split_lines, analysis_function, analysis_docstring
from adapter import Adapter
from format import File, DocstringStyle


def main():
    """Console script for merlion."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    # print("Arguments: " + str(args._))
    # print("Replace this message by putting your code into "
    #       "merlion.cli.main")

    res = split_lines("./parser.py")
    res = analysis_function(res)
    res = analysis_docstring(res)

    adpt = Adapter()
    adpt.adapter(res)

    file = File(input_file_name="parser.py", docs_list=adpt.docstrings, target_style=DocstringStyle.Numpydoc)
    file.format()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
