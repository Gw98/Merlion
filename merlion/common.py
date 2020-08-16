import typing
import enum

class DocstringElementType(enum.Enum):
    Summary = 1, 
    Description = 2,
    Param = 3,
    Return = 4,
    Raise = 5, 
    Example = 6,
    Attribute = 7,
    TODO = 8,
    Yield = 9,
    Note = 10


class DocstringMeta:
    def __init__(
        self,
        args: typing.List[str],
        description: typing.Optional[str]
    ) -> None:
        self.args = args
        self.description = description


class DocstringParam(DocstringMeta):
    def __init__(
        self,
        args: typing.List[str],
        description: typing.Optional[str],
        param_name: str,
        type_name: typing.Optional[str]
    ) -> None:
        super().__init__(args, description)
        self.param_name = param_name
        self.type_name = type_name


class DocstringReturn(DocstringMeta):
    """ Returns for function, or Yields for generators
    """

    def __init__(
        self,
        args: typing.List[str],
        description: typing.Optional[str],
        return_name: typing.Optional[str],
        type_name: typing.Optional[str],
        is_generator: bool
    ) -> None:
        super().__init__(args, description)
        self.return_name = return_name
        self.type_name = type_name
        self.is_generator = is_generator


class DocstringRaise(DocstringMeta):
    def __init__(
        self,
        args: typing.List[str],
        description: typing.Optional[str],
        type_name: typing.Optional[str]
    ) -> None:
        super().__init__(args, description)
        self.type_name = type_name


class DocstringElement:
    def __init__(
        self,
        type: DocstringElementType,
        element: typing.Union[DocstringParam, DocstringReturn, DocstringRaise]
    ) -> None:
        self.type = type,
        self.element = element


class Docstring:
    def __init__(self) -> None:
        pass
