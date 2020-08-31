"""
Note for adapter:
    1. the values in config(see line 18) should be the written from the args in the command line
    2. for rtype section in reST and Epytext:
        there should be an element like this:
        DocstringElement(type = DocstringElementType.Rtype, description = "bool")
    3. the class File has a new member called quote, the value of quote should be "\'" or "\""
"""


import typing
import enum
import inflect
import textwrap
import os
import difflib

config = {'origin_tab_space_cnt': 4, 'tab_space_cnt': 4, 'max_char': 80}


@enum.unique
class DocstringElementType(enum.Enum):
    Param = enum.auto(),
    Type = enum.auto(),
    Return = enum.auto(),
    Rtype = enum.auto()
    Raise = enum.auto(),
    Example = enum.auto(),
    Module_Attribute = enum.auto(),
    Class_Attribute = enum.auto(),
    Todo = enum.auto(),
    Yield = enum.auto(),
    Note = enum.auto(),
    Receive = enum.auto(),
    Warn = enum.auto(),
    SeeAlso = enum.auto(),
    Reference = enum.auto()
    Var = enum.auto(),
    VarType = enum.auto(),


@enum.unique
class DocstringStyle(enum.Enum):
    Google = enum.auto(),
    Numpydoc = enum.auto(),
    reST = enum.auto()
    Epytext = enum.auto()


class DocstringParam():
    """ Args for function, or Module level variable for module(in the Arrtibute section of the module docstring)

    Attributes:
        param_name(str): the parameter's name
        type_name(typing.Optional[str]): the parameter's type
        default_value(typing.Optional[str]): the parameter's default value
        description: the description of the parameter
    """

    def __init__(
        self,
        param_name: str,
        type_name: typing.Optional[str] = None,
        default_value: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
    ) -> None:
        self.param_name = param_name
        self.type_name = type_name
        self.default_value = default_value
        self.description = description
        if not type_name:
            self.type_name = None
        if not default_value:
            self.default_value = None
        if not description:
            self.description = None

    def _strip(self) -> None:
        self.param_name = str(self.param_name).strip()
        if self.type_name is not None:
            self.type_name = str(self.type_name).strip()
        if self.default_value is not None:
            self.default_value = str(self.default_value).strip()
        if self.description is not None:
            self.description = str(self.description).strip()


class DocstringReturn():
    """ Returns for functions, or Yields for generators

    Attributes:
        return_name(typing.Optional[str]): the name of return variable
        type_name(typing.Optional[str]): the type of return value
        description(typing.Optional[str]): the description of the return value for functions, or the yield for generators
    """

    def __init__(
        self,
        return_name: typing.Optional[str] = None,
        type_name: typing.Optional[str] = None,
        description: typing.Optional[str] = None
    ) -> None:
        self.return_name = return_name
        self.type_name = type_name
        self.description = description
        if not return_name:
            self.return_name = None
        if not type_name:
            self.type_name = None
        if not description:
            self.description = None

    def _strip(self) -> None:
        if self.return_name is not None:
            self.return_name = str(self.return_name).strip()
        if self.type_name is not None:
            self.type_name = str(self.type_name).strip()
        if self.description is not None:
            self.description = str(self.description).strip()


class DocstringRaise():
    """ Raises for Exceptions

    Attributes:
        type_name(typing.Optional[str]): the type of exception
        description(typing.Optional[str]): the description of the exception
    """

    def __init__(
        self,
        type_name: str,
        description: typing.Optional[str] = None
    ) -> None:
        self.type_name = type_name
        self.description = description
        if not description:
            self.description = None

    def _strip(self) -> None:
        self.type_name = str(self.type_name).strip()
        if self.description is not None:
            self.description = str(self.description).strip()

# TODO: quote, empty str, string divede


class DocstringOther():
    """Example, Todo, Note ...

    form 1: name: description(e.g. Todo)
    form 2: single_description(e.g. Note)
    """

    def __init__(
        self,
        name: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        single_description: typing.Optional[str] = None
    ) -> None:
        self.name = name
        self.description = description
        self.single_description = single_description
        if not name:
            self.name = None
        if not description:
            self.description = None
        if not single_description:
            self.single_description = None

    def _strip(self) -> None:
        if self.name is not None:
            self.name = str(self.name).strip()
        if self.description is not None:
            self.description = str(self.description).strip()
        if self.single_description is not None:
            self.single_description = str(self.single_description).strip()


class DocstringElement:
    """wrapper

    Attributes:
        elem_type(DocstringElementType): the type of the element
        content: the node that was wrappered. It's type is DocstringParam, DocstringReturn, DocstringRaise or DocstringOther
    """

    def __init__(
        self,
        elem_type: DocstringElementType,
        content: typing.Union[DocstringParam,
                              DocstringReturn,
                              DocstringRaise,
                              DocstringOther] = None
    ) -> None:
        self.elem_type = elem_type
        self.content = content

    def _strip(self) -> None:
        self.content._strip()


class Docstring:
    """the abstraction of a docstring

    Attributes:
        start_line(int): this docstring was in [start_line, end_line) in the origin program. The index of line start from 0.
        tab_cnt(int): this docstring's first line begins with tab_cnt tabs
        quote(str = "\""): the quote of the docstring, \' or \", the default is \"
        summary: the short summary, usually the first line of the docstring
        description: the longer and detailed description, usually the second paragraph of the docstring

    """

    def __init__(
        self,
        start_line: int,
        end_line: int,
        tab_cnt: int,
        quote: str = "\"",
        summary: typing.Optional[str] = None,
        description: typing.Optional[str] = None
    ) -> None:
        self.summary = summary
        self.description = description
        self.elements: typing.List[DocstringElement] = []
        self.start_line = start_line
        self.end_line = end_line
        self.tab_cnt = tab_cnt
        self.quote = quote

    def _strip(self) -> None:
        if self.summary is not None:
            self.summary = str(self.summary).strip()
        if self.description is not None:
            self.description = str(self.description).strip()
        for elem in self.elements:
            elem._strip()

    def _getSpecificTypeElement(
        self,
        elem_type: DocstringElementType
    ) -> typing.List[DocstringElement]:
        return [elem for elem in self.elements if elem.elem_type is elem_type]

    def _addDescription(self) -> None:
        if self.summary is None:
            self.summary = "This is summary."
        if self.description is None:
            self.description = "This is more detailed description."
        for elem_type in DocstringElementType:
            elems = self._getSpecificTypeElement(elem_type)
            for i, elem in enumerate(elems):
                content = elem.content
                if (isinstance(content, DocstringOther) and content.name is None) or (content.description is not None):
                    continue
                content.description = generateDescription(i, elem)

    def _googleFormat(self) -> typing.List[str]:
        self._strip()
        self._addDescription()
        output: typing.List[str] = []
        tab: str = ' ' * config['tab_space_cnt']
        tabs: str = tab * self.tab_cnt

        # summary
        appendString2List(
            output, self.quote * 3 + self.summary, self.tab_cnt, 0)
        output.append("\n")

        # description
        appendString2List(
            output, self.description, self.tab_cnt, 0)
        output.append("\n")

        # others
        for elem_type in DocstringElementType:
            elems = self._getSpecificTypeElement(elem_type)
            if len(elems) == 0:
                continue
            # section name
            section_name = getSectionName(
                elems, elem_type, DocstringStyle.Google)
            output.append(tabs + section_name + ":" + "\n")
            # content
            for elem in elems:
                content = elem.content
                string: str = None
                if isinstance(content, DocstringParam):
                    if content.type_name is not None:
                        string = content.param_name + \
                            " (" + content.type_name + "): " + \
                            content.description
                    else:
                        string = content.param_name + ": " + content.description
                elif isinstance(content, DocstringReturn):
                    if content.type_name is not None:
                        string = content.type_name + ": " + content.description
                    else:
                        string = content.description
                elif isinstance(content, DocstringRaise):
                    string = content.type_name + ": " + content.description
                elif isinstance(content, DocstringOther):
                    if content.name is None and content.description is None:
                        string = content.single_description
                    elif content.name is None and content.description is not None:
                        string = content.description
                    elif content is not None:
                        string = content.name + ": " + content.description
                appendString2List(
                    output, string, self.tab_cnt + 1, 1)
            output.append("\n")

        output.append(tabs + self.quote * 3 + "\n")
        return output

    def _numpydocFormat(self) -> typing.List[str]:
        self._strip()
        self._addDescription()
        output: typing.List[str] = []
        tab: str = ' ' * config['tab_space_cnt']
        tabs: str = tab * self.tab_cnt

        # summary
        appendString2List(
            output, self.quote * 3 + self.summary, self.tab_cnt, 0)
        output.append("\n")

        # description
        appendString2List(
            output, self.description, self.tab_cnt, 0)
        output.append("\n")

        # others
        for elem_type in DocstringElementType:
            elems = self._getSpecificTypeElement(elem_type)
            if len(elems) == 0:
                continue
            # section name
            section_name = getSectionName(
                elems, elem_type, DocstringStyle.Numpydoc)
            output.append(tabs + section_name + "\n")
            output.append(tabs + "-" * len(section_name) + "\n")
            # content
            for elem in elems:
                content = elem.content
                string_0: str = None
                string_1: str = None
                type_name: str = " : "
                if isinstance(content, DocstringParam):
                    if content.type_name is not None:
                        type_name += content.type_name
                    string_0 = content.param_name + type_name
                    string_1 = content.description
                elif isinstance(content, DocstringReturn):
                    if content.type_name is not None:
                        type_name += content.type_name
                    if content.return_name is not None:
                        string_0 = content.return_name + type_name
                    else:
                        string_0 = content.type_name
                    string_1 = content.description
                elif isinstance(content, DocstringRaise):
                    string_0 = content.type_name
                    string_1 = content.description
                elif isinstance(content, DocstringOther):
                    if elem_type == DocstringElementType.SeeAlso:
                        appendString2List(
                            output, content.name + " : " + content.description, self.tab_cnt, 1)
                        continue
                    if content.name is None and content.description is None:
                        string_0 = content.single_description
                        string_1 = None
                    elif content.name is None and content.description is not None:
                        string_0 = content.description
                        string_1 = None
                    elif content is not None:
                        string_0 = content.name
                        string_1 = content.description

                if string_0 is not None:
                    appendString2List(
                        output, string_0, self.tab_cnt, 0)
                if string_1 is not None:
                    appendString2List(
                        output, string_1, self.tab_cnt + 1, 0)
            output.append("\n")

        output.append(tabs + self.quote * 3 + "\n")
        return output

    def _reST_or_epytext_Format(self, style: DocstringStyle) -> typing.List[str]:
        self._strip()
        self._addDescription()
        output: typing.List[str] = []
        tab: str = ' ' * config['tab_space_cnt']
        tabs: str = tab * self.tab_cnt

        flag: str = ""
        if (style == DocstringStyle.reST):
            flag = ":"
        else:
            flag = "@"

        # summary
        appendString2List(
            output, self.quote * 3 + self.summary, self.tab_cnt, 0)
        output.append("\n")

        # description
        appendString2List(
            output, self.description, self.tab_cnt, 0)
        output.append("\n")

        # others
        for elem_type in DocstringElementType:
            elems = self._getSpecificTypeElement(elem_type)
            if len(elems) == 0:
                continue
            # section name
            section_name = getSectionName(
                elems, elem_type, DocstringStyle.reST)
            # output.append(tabs + section_name + ":" + "\n")
            # content
            for elem in elems:
                content = elem.content
                string: str = None
                if isinstance(content, DocstringParam):
                    if content.type_name is not None:
                        if style == DocstringStyle.reST:
                            string = flag + section_name + " " + content.type_name + \
                                " " + content.param_name + ": " + content.description
                        else:
                            string = flag + section_name + " " + content.param_name + \
                                ": " + content.type_name + ": " + content.description
                    else:
                        string = flag + section_name + " " + \
                            content.param_name + ": " + content.description
                elif isinstance(content, DocstringReturn):
                    string = flag + section_name + ": " + content.description
                elif isinstance(content, DocstringRaise):
                    string = flag + section_name + " " + \
                        content.type_name + ": " + content.description
                elif isinstance(content, DocstringOther):
                    if content.name is None and content.description is None:
                        string = flag + section_name + ": " + content.single_description
                    elif content.name is None and content.description is not None:
                        string = flag + section_name + ": " + content.description
                    elif content is not None:
                        string = flag + section_name + " " + content.name + ": " + content.description
                appendString2List(
                    output, string, self.tab_cnt + 1, 1)

        output.append(tabs + self.quote * 3 + "\n")
        return output

    def format(
        self,
        style: DocstringStyle
    ) -> typing.List[str]:
        if style == DocstringStyle.Google:
            return self._googleFormat()
        elif style == DocstringStyle.Numpydoc:
            return self._numpydocFormat()
        elif style == DocstringStyle.reST or style == DocstringStyle.Epytext:
            return self._reST_or_epytext_Format(style)
        return []


class File:
    """the abstraction of a input file

    Attributes:
        input_file_name(str = None): the name of the input file (only name! you can initial it with a path,
            it will automatically get the filename)
        source_path(str = ""): the input file's path, or anything you want to show as source path in diff
        target_path(str = ""): the target file's path, or anything you want to show as target path in diff
        prog(typing.List[str]): the origin program, read from input file
        quote(str = "\""): the quote of the docstring, \' or \", the default is \"
        docs_list(typing.List[Docstring]): the docstrings in this file
        target_style(DocstringStyle): the target format style. Supporting Google and Numpydoc now.

    """

    def __init__(
        self,
        input_file_name: str = None,  # input file's name
        source_path: str = "",
        target_path: str = "",
        prog: typing.List[str] = [],
        quote: str = "\"",
        docs_list: typing.List[Docstring] = [],
        target_style: DocstringStyle = None
    ) -> None:
        self.input_file_name = os.path.basename(input_file_name)

        if source_path.startswith(os.sep):
            source_path = source_path[1:]
        if source_path and not source_path.endswith(os.sep):
            source_path += os.sep
        if target_path.startswith(os.sep):
            target_path = target_path[1:]
        if target_path and not target_path.endswith(os.sep):
            target_path += os.sep
        self.source_path = source_path
        self.target_path = target_path
        self.prog = prog
        self.quote = quote
        self.docs_list = docs_list
        self.target_style = target_style

    def _diff(self) -> typing.List[str]:
        formatted_prog = self._getFormattedProgram()

        from_file = 'a/' + self.source_path + self.input_file_name
        to_file = 'b/' + self.target_path + self.input_file_name
        diff_list = difflib.unified_diff(
            self.prog, formatted_prog, from_file, to_file)
        return diff_list

    def _getFormattedProgram(self) -> typing.List[str]:
        pre: int = 0  # line[0, pre - 1] of origin program is formatted
        formatted_prog: typing.List[str] = []
        formatted_docs: typing.List[str] = []
        for docs in self.docs_list:
            docs.quote = self.quote
            if docs.start_line > pre:
                formatted_prog.extend(self.prog[pre:docs.start_line])
            formatted_docs = docs.format(self.target_style)
            formatted_prog.extend(formatted_docs)
            pre = docs.end_line
        formatted_prog.extend(self.prog[pre:])

        return formatted_prog

    def format(self) -> None:
        diff_list = self._diff()
        patch_file = self.input_file_name + ".patch"
        with open(patch_file, 'w') as f:
            f.writelines(diff_list)


type2word: typing.Dict[DocstringElementType, str] = {
    DocstringElementType.Param: "parameter",
    DocstringElementType.Return: "return value",
    DocstringElementType.Raise: "possible exception",
    DocstringElementType.Example: "example",
    DocstringElementType.Module_Attribute: "module level variable",
    DocstringElementType.Class_Attribute: "class level variable",
    DocstringElementType.Todo: "TODO",
    DocstringElementType.Yield: "yield",
    DocstringElementType.Note: "note",
    DocstringElementType.Receive: "receive value",
    DocstringElementType.Warn: "warning",
    DocstringElementType.SeeAlso: "see also message",
    DocstringElementType.Reference: "reference",
    DocstringElementType.Type: "type",
    DocstringElementType.Var: "variable",
    DocstringElementType.VarType: "variable type",
    DocstringElementType.Rtype: "return type"
}

type2section_single: typing.Dict[DocstringStyle, typing.Dict[DocstringElementType, str]] = {
    DocstringStyle.Google: {
        DocstringElementType.Param: "Arg",
        DocstringElementType.Return: "Return",
        DocstringElementType.Raise: "Raise",
        DocstringElementType.Example: "Example",
        DocstringElementType.Module_Attribute: "Attribute",
        DocstringElementType.Class_Attribute: "Attribute",
        DocstringElementType.Todo: "Todo",
        DocstringElementType.Yield: "Yield",
        DocstringElementType.Note: "Note",
        DocstringElementType.Receive: "Receive",
        DocstringElementType.Warn: "Warn",
        DocstringElementType.SeeAlso: "See Also",
        DocstringElementType.Reference: "Reference"
    },
    DocstringStyle.Numpydoc: {
        DocstringElementType.Param: "Parameter",
        DocstringElementType.Return: "Return",
        DocstringElementType.Raise: "Raise",
        DocstringElementType.Example: "Example",
        DocstringElementType.Module_Attribute: "Attribute",
        DocstringElementType.Class_Attribute: "Attribute",
        DocstringElementType.Todo: "Todo",
        DocstringElementType.Yield: "Yield",
        DocstringElementType.Note: "Note",
        DocstringElementType.Receive: "Receive",
        DocstringElementType.Warn: "Warn",
        DocstringElementType.SeeAlso: "See Also",
        DocstringElementType.Reference: "Reference"
    },
    DocstringStyle.reST: {
        DocstringElementType.Param: "param",
        DocstringElementType.Type: "type",
        DocstringElementType.Raise: "raise",
        DocstringElementType.Var: "var",
        DocstringElementType.VarType: "vartype",
        DocstringElementType.Return: "return",
        DocstringElementType.Rtype: "rtype",
        DocstringElementType.Example: "example",
        DocstringElementType.Module_Attribute: "attribute",
        DocstringElementType.Class_Attribute: "attribute",
        DocstringElementType.Todo: "todo",
        DocstringElementType.Yield: "yield",
        DocstringElementType.Note: "note",
        DocstringElementType.Receive: "receive",
        DocstringElementType.Warn: "warn",
        DocstringElementType.SeeAlso: "see also",
        DocstringElementType.Reference: "reference"
    }
}

type2section_plural: typing.Dict[DocstringStyle, typing.Dict[DocstringElementType, str]] = {
    DocstringStyle.Google: {
        DocstringElementType.Param: "Args",
        DocstringElementType.Return: "Returns",
        DocstringElementType.Raise: "Raises",
        DocstringElementType.Example: "Examples",
        DocstringElementType.Module_Attribute: "Attributes",
        DocstringElementType.Class_Attribute: "Attributes",
        DocstringElementType.Todo: "Todos",
        DocstringElementType.Yield: "Yields",
        DocstringElementType.Note: "Notes",
        DocstringElementType.Receive: "Receives",
        DocstringElementType.Warn: "Warns",
        DocstringElementType.SeeAlso: "See Also",
        DocstringElementType.Reference: "References"
    },
    DocstringStyle.Numpydoc: {
        DocstringElementType.Param: "Parameters",
        DocstringElementType.Return: "Returns",
        DocstringElementType.Raise: "Raises",
        DocstringElementType.Example:  "Examples",
        DocstringElementType.Module_Attribute: "Attributes",
        DocstringElementType.Class_Attribute: "Attributes",
        DocstringElementType.Todo: "Todos",
        DocstringElementType.Yield: "Yields",
        DocstringElementType.Note: "Notes",
        DocstringElementType.Receive: "Receives",
        DocstringElementType.Warn: "Warns",
        DocstringElementType.SeeAlso: "See Alsos",
        DocstringElementType.Reference: "References"
    },
    DocstringStyle.reST: {  # for reST single and plural are the same
        DocstringElementType.Param: "param",
        DocstringElementType.Type: "type",
        DocstringElementType.Raise: "raise",
        DocstringElementType.Var: "var",
        DocstringElementType.VarType: "vartype",
        DocstringElementType.Return: "return",
        DocstringElementType.Rtype: "rtype",
        DocstringElementType.Example: "example",
        DocstringElementType.Module_Attribute: "attribute",
        DocstringElementType.Class_Attribute: "attribute",
        DocstringElementType.Todo: "todo",
        DocstringElementType.Yield: "yield",
        DocstringElementType.Note: "note",
        DocstringElementType.Receive: "receive",
        DocstringElementType.Warn: "warn",
        DocstringElementType.SeeAlso: "see also",
        DocstringElementType.Reference: "reference"
    }
}


def generateDescription(id: int, elem: DocstringElement) -> str:
    engine = inflect.engine()
    string: str = "The " + engine.ordinal(id) + " " + type2word[elem.elem_type]
    if (isinstance(elem.content, DocstringParam) and elem.content.default_value is not None):
        string = string + "The default value is " + elem.content.default_value
    return string


def appendString2List(lst: typing.List[str], message: str, prefix_tab_cnt: int, mult_line_tab_cnt: int) -> None:
    strings: typing.List[str] = message.splitlines()
    leading_tab_cnt: typing.List[int] = []
    for i, string in enumerate(strings):
        if i == 0:
            leading_tab_cnt.append(prefix_tab_cnt)
        else:
            leading_tab_cnt.append(
                max(int((len(string) - len(string.lstrip(' '))) /
                        config['origin_tab_space_cnt']), prefix_tab_cnt + mult_line_tab_cnt))
        strings[i] = string.strip()

    tab: str = ' ' * config['tab_space_cnt']
    prefix: str = tab * prefix_tab_cnt
    remain: str = ""
    remain_leading_tab_cnt: int = 0
    max_char: int = config['max_char']

    for i, string in enumerate(strings):
        if remain:
            if remain_leading_tab_cnt == leading_tab_cnt[i]:
                string = remain + string
            else:
                lst.append(prefix + remain + "\n")

        prefix = tab * leading_tab_cnt[i]
        idx: int = 0
        while len(string) > max_char - len(prefix):
            if i == 0 and idx == 1:
                prefix = prefix + tab * mult_line_tab_cnt
            lst.append(prefix + string[:max_char - len(prefix)] + "\n")
            string = string[max_char - len(prefix):]
            idx += 1

        remain = string
        if i == 0 and idx >= 1:
            remain_leading_tab_cnt = prefix_tab_cnt + mult_line_tab_cnt
        else:
            remain_leading_tab_cnt = leading_tab_cnt[i]

    if remain:
        lst.append(tab * remain_leading_tab_cnt + remain + "\n")


def getSectionName(elems: typing.List[DocstringElement], elem_type: DocstringElementType, style: DocstringStyle) -> str:
    if len(elems) == 0:
        return None
    elif len(elems) == 1:
        return type2section_single[style][elem_type]
    else:
        return type2section_plural[style][elem_type]