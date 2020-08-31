"""Console script for merlion."""
import argparse
import os
import sys
from parser import analysis_docstring, analysis_function, split_lines

from adapter import Adapter
from format import DocstringStyle, File

STYLE_TABLE = {
    'Google': DocstringStyle.Google,
    'Numpydoc': DocstringStyle.Numpydoc,
    'reST': DocstringStyle.reST,
    'Epytext': DocstringStyle.Epytext
}


def main():
    """Console script for merlion."""
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--docstyle', default='Numpydoc')
    args = parser.parse_args()

    if not os.path.exists(args.filename):
        raise Exception('[Error] can not find file: {}'.format(args.filename))

    target_style = STYLE_TABLE.get(args.docstyle, None)
    if not target_style:
        raise Exception('[Error] invalid docstring style : {}.\n Please Select in Numpydoc, Google, reST or Epytext.'.format(args.docstyle))

    import pdb
    pdb.set_trace()

    res = split_lines(args.filename)
    res = analysis_function(res)
    res = analysis_docstring(res)

    adpt = Adapter()
    adpt.adapter(res)

    with open(args.filename, 'r') as f:
        source = f.read()
    prog = source.splitlines(keepends=True)


    # File.program is needed
    file = File(input_file_name=args.filename, docs_list=adpt.docstrings,
                target_style=target_style, prog=prog)
    file.format()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
