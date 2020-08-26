"""[summary]
"""
import difflib
import fnmatch
import os

from formatter import NumpydocFormatter, GoogleFormatter, reSTFormatter
from parser import NumpydocParser, GoogleParser, reSTParser

from redbaron.nodes import ClassNode, CommentNode, DefNode, StringNode
from redbaron.redbaron import RedBaron


PARSER_STYLE_LIST = {
    'google': GoogleParser,
    'numpy': NumpydocParser,
    'reST': reSTParser,
}


FORMATTER_STYLE_LIST = {
    'google': GoogleFormatter,
    'numpy': NumpydocFormatter,
    'reST': reSTFormatter,
}


class Merlion(object):
    """[summary]

    Args:
        object ([type]): [description]
    """
    def __init__(self):
        """[summary]
        """
        self.paths = {}
        self.dstpaths = {}

        self.parser = PARSER_STYLE_LIST['numpy']()
        self.formatter = FORMATTER_STYLE_LIST['google']()


    def load(self, dirs, patterns=['*.py', '*.pyi'], ignores=None):
        """[summary]

        Args:
            dirs ([type]): [description]
            patterns (list, optional): [description]. Defaults to ['*.py', '*.pyi'].
            ignores ([type], optional): [description]. Defaults to None.
        """
        if not ignores:
            ignores = []

        if isinstance(dirs, str):
            dirs = [dirs]

        if isinstance(patterns, str):
            patterns = [patterns]
            
        if isinstance(ignores, str):
            ignores = [ignores]

        paths = []
        for dir in dirs:
            # TODO file not exists
            if os.path.isfile(dir):
                paths.append(dir)
            else:
                for root, _, files in os.walk(dir):
                    for filename in files:
                        paths.append(os.path.join(root, filename))

        paths = [path for path in paths if self.filter_files(path, patterns, ignores)]

        for path in paths:
            source = self.read_file(path)
            self.paths[path] = source


    def filter_files(self, filename, patterns, ignores):
        """[summary]

        Args:
            filename ([type]): [description]
            patterns ([type]): [description]
            ignores ([type]): [description]

        Returns:
            [type]: [description]
        """
        if not self.match_patterns(filename, patterns):
            return False
        if self.match_patterns(filename, ignores):
            return False
        return True


    def match_patterns(self, filename, patterns):
        """[summary]

        Args:
            filename ([type]): [description]
            patterns ([type]): [description]

        Returns:
            [type]: [description]
        """
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False


    def read_file(self, path):
        """[summary]

        Args:
            path ([type]): [description]

        Returns:
            [type]: [description]
        """
        with open(path, 'r') as f:
            source = f.read()

        return source

    
    def map(self):
        """[summary]
        """
        for path, source in self.paths.items():
            # TODO fst parse error
            node = RedBaron(source)
            self.process(node)
            self.dstpaths[path] = node.dumps()


    def process(self, node):
        """[summary]

        Args:
            node ([type]): [description]
        """
        self.process_module(node)

        clsnodes = node.find_all('ClassNode')
        for clsnode in clsnodes:
            self.process_class(clsnode)

        funcnodes = node.find_all('DefNode')
        for funcnode in funcnodes:
            self.process_func(funcnode)


    def process_module(self, node):
        docstring_node = self.get_docstring_node(node)
        if docstring_node:
            self.process_node_with_docstring(docstring_node)


    def process_class(self, node):
        docstring_node = self.get_docstring_node(node)
        if docstring_node:
            self.process_node_with_docstring(docstring_node)


    def process_func(self, node):
        docstring_node = self.get_docstring_node(node)
        if docstring_node:
            self.process_node_with_docstring(docstring_node)


    def get_docstring_node(self, node):
        """[summary]

        Args:
            node ([type]): [description]

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        if not isinstance(node, RedBaron) and not isinstance(node, ClassNode) and not isinstance(node, DefNode):
            raise Exception('object without docstring')
        for subnode in node:
            if isinstance(subnode, StringNode):
                return subnode
            if isinstance(subnode, CommentNode):
                continue
            return None


    def process_node_with_docstring(self, node):
        """[summary]

        Args:
            node ([type]): [description]

        Raises:
            Exception: [description]
        """
        if not isinstance(node, StringNode): 
            raise Exception('invalide string node')
        indent = 0  # TODO
        docstring = self.parser.parse(node.value)
        node.value = self.formatter.format(docstring)

    
    def output(self):
        for path, dst in self.dstpaths.items():
            source = self.paths[path]
            patches = difflib.unified_diff(
                source.rstrip().splitlines(True), 
                dst.rstrip().splitlines(True),
                'a/{}'.format(path),
                'b/{}'.format(path)
                )
            with open('{}.patch'.format(path), 'w') as f:
                f.writelines(patches)


    