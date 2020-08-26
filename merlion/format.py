import typing
import enum
import inflect
import textwrap
import os
import difflib


@enum.unique
class DocstringElementType(enum.Enum):
    Param = enum.auto(),
    Return = enum.auto(),
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


@enum.unique
class DocstringStyle(enum.Enum):
    Google = enum.auto(),
    Numpydoc = enum.auto(),
    reST = enum.auto()


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

    def _strip(self) -> None:
        self.param_name = self.param_name.strip()
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

    def _strip(self) -> None:
        self.type_name = str(self.type_name).strip()
        if self.description is not None:
            self.description = str(self.description).strip()


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
        start_line(int): this docstring was in [start_line, end_line) in the origin program
        tab_cnt(int): this docstring's first line begins with tab_cnt tabs
        summary: the short summary, usually the first line of the docstring
        description: the longer and detailed description, usually the second paragraph of the docstring

    """

    def __init__(
        self,
        start_line: int,
        end_line: int,
        tab_cnt: int,
        summary: typing.Optional[str] = None,
        description: typing.Optional[str] = None
    ) -> None:
        self.summary = summary
        self.description = description
        self.elements: typing.List[DocstringElement] = []
        self.start_line = start_line
        self.end_line = end_line
        self.tab_cnt = tab_cnt

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
        max_char: int = config['max_char']

        # summary
        appendWarppedString2List(
            output, "\"\"\"" + self.summary, max_char, tabs, "")
        output.append("\n")

        # description
        appendWarppedString2List(
            output, self.description, max_char, tabs, "")
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
                    string = content.type_name + ": " + content.description
                elif isinstance(content, DocstringRaise):
                    string = content.type_name + ": " + content.description
                elif isinstance(content, DocstringOther):
                    if content.name is None and content.description is None:
                        string = content.single_description
                    elif content.name is None and content.description is not None:
                        string = content.description
                    elif content is not None:
                        string = content.name + ": " + content.description
                appendWarppedString2List(
                    output, string, max_char, tabs + tab, tab)
            output.append("\n")

        output.append(tabs + "\"\"\"" + "\n")
        return output

    def _numpydocFormat(self) -> typing.List[str]:
        self._strip()
        self._addDescription()
        output: typing.List[str] = []
        tab: str = ' ' * config['tab_space_cnt']
        tabs: str = tab * self.tab_cnt
        max_char: int = config['max_char']

        # summary
        appendWarppedString2List(
            output, "\"\"\"" + self.summary, max_char, tabs, "")
        output.append("\n")

        # description
        appendWarppedString2List(
            output, self.description, max_char, tabs, "")
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
                        appendWarppedString2List(
                            output, content.name + " : " + content.description, max_char, tabs, " " * len(content.name + " : "))
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
                    appendWarppedString2List(
                        output, string_0, max_char, tabs, "")
                if string_1 is not None:
                    appendWarppedString2List(
                        output, string_1, max_char, tabs + tab, "")
            output.append("\n")

        output.append(tabs + "\"\"\"" + "\n")
        return output

    def format(
        self,
        style: DocstringStyle
    ) -> typing.List[str]:
        if style == DocstringStyle.Google:
            return self._googleFormat()
        elif style == DocstringStyle.Numpydoc:
            return self._numpydocFormat()
        return []


class File:
    """the abstraction of a input file

    Attributes:
        input_file_name(str = None): the name of the input file (only name! you can initial it with a path, 
            it will automatically get the filename)
        source_path(str = ""): the input file's path, or anything you want to show as source path in diff
        target_path(str = ""): the target file's path, or anything you want to show as target path in diff
        prog(typing.List[str]): the origin program, read from input file
        docs_list(typing.List[Docstring]): the docstrings in this file
        target_style(DocstringStyle): the target format style. Supporting Google and Numpydoc now.

    """

    def __init__(
        self,
        input_file_name: str = None,  # input file's name
        source_path: str = "",
        target_path: str = "",
        prog: typing.List[str] = [],
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
        self.docs_list = docs_list
        self.target_style = target_style

    def _diff(self) -> typing.List[str]:
        formatted_prog = self._getFormattedProgram()

        from_file = 'a/' + self.source_path + self.input_file_name
        to_file = 'b/' + self.target_path + self.input_file_name
        diff_list = difflib.unified_diff(
            self.prog, formatted_prog, from_file, to_file)
        # return [d for d in diff_list]
        return diff_list

    def _getFormattedProgram(self) -> typing.List[str]:
        pre: int = 0  # line[0, pre - 1] of origin program is formatted
        formatted_prog: typing.List[str] = []
        formatted_docs: typing.List[str] = []
        for docs in self.docs_list:
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
    DocstringElementType.Reference: "reference"
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
    }
}


def generateDescription(id: int, elem: DocstringElement) -> str:
    engine = inflect.engine()
    string: str = "The " + engine.ordinal(id) + type2word[elem.elem_type]
    if (isinstance(elem.content, DocstringParam) and elem.content.default_value is not None):
        string = string + "The default value is " + elem.content.default_value
    return string


config = {'tab_space_cnt': 4, 'max_char': 80}


def appendWarppedString2List(lst: typing.List[str], string: str, max_char: int, prefix: str, mult_line_tab: str) -> None:
    lst.append(prefix + string[:max_char - len(prefix)] + "\n")
    if len(string) - 1 < max_char - len(prefix):
        return
    warpped_lines: typing.List[str] = textwrap.wrap(
        string[max_char - len(prefix):], max_char - len(prefix) - len(mult_line_tab))
    for line in warpped_lines:
        lst.append(mult_line_tab + prefix + line + "\n")


def getSectionName(elems: typing.List[DocstringElement], elem_type: DocstringElementType, style: DocstringStyle) -> str:
    if len(elems) == 0:
        return None
    elif len(elems) == 1:
        return type2section_single[style][elem_type]
    else:
        return type2section_plural[style][elem_type]
