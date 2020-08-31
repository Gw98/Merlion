"""Console script for merlion."""
import argparse
import sys


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

    res = split_lines("test_case.py")
    res = analysis_function(res)
    res = analysis_docstring(res)

    adpt = Adapter()
    adpt.adapter(res)

    with open('test_case.py', 'r') as f:
        source = f.read()
    import pdb
    pdb.set_trace()
    prog = source.splitlines(keepends=True)

    # File.program is needed
    file = File(input_file_name="test_case.py", docs_list=adpt.docstrings,
                target_style=DocstringStyle.Numpydoc, prog=prog)
    file.format()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
