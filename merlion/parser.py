# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from enum import Enum
import re


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def load_file(path):
    with open(path) as file:
        return file.readlines()


class ItemType(Enum):
    Function = 0
    Docstring = 1
    Normal = 2


class Item:
    def __init__(self, start=0, end=0, types=ItemType.Normal, text="", info={}):
        self.types = types
        self.start = start
        self.end = end
        self.text = text
        self.info = info


class State(Enum):
    Normal = 0
    FindDeclaration = 1
    FindDocstring = 2


def split_lines(path) -> [Item]:
    """ 分离不同代码段
    这个函数可以按行
    分离不同类型的代码

    :param path: str: 输入文件目录
    :return split_lines: str: 分离后的代码
    """
    lines = load_file(path)
    ret = []
    state = State.Normal
    start = 0
    text = ''
    lim = '"""'
    for index in range(len(lines)):
        l = lines[index].strip()
        if state == State.Normal:
            if l.startswith('"""') or l.startswith("'''"):
                if text != '':
                    ret.append(Item(start=start, end=index - 1, types=ItemType.Normal, text=text))
                    start = index
                    text = ''
                if l.startswith('"""'):
                    lim = '"""'
                else:
                    lim = "'''"
                state = State.FindDocstring
                text += lines[index]
                if l.count(lim) == 2:
                    state = State.Normal
                    ret.append(Item(start=start, end=index, types=ItemType.Docstring, text=text))
                    start = index + 1
                    text = ''

            elif l.startswith('def ') or l.startswith('class ') or l.startswith('async def'):
                if text != '':
                    ret.append(Item(start=start, end=index - 1, types=ItemType.Normal, text=text))
                    start = index
                    text = ''
                state = State.FindDeclaration
                text += lines[index]
                if re.search(r''':(|\s*#[^'"]*)$''', l):
                    state = State.Normal
                    ret.append(Item(start=start, end=index, types=ItemType.Function, text=text))
                    start = index + 1
                    text = ''
            else:
                text += lines[index]
        elif state == State.FindDeclaration:
            text += lines[index]
            if re.search(r''':(|\s*#[^'"]*)$''', l):
                state = State.Normal
                end = index
                ret.append(Item(start=start, end=end, types=ItemType.Function, text=text))
                start = index + 1
                text = ''
        elif state == State.FindDocstring:
            text += lines[index]
            if lim in l:
                state = State.Normal
                ret.append(Item(start=start, end=index, types=ItemType.Docstring, text=text, info={"lim": lim}))
                start = index + 1
                text = ''
    if text != '':
        if state == State.Normal:
            ret.append(Item(start=start, end=len(lines), types=ItemType.Normal, text=text))
        elif state == State.FindDeclaration:
            ret.append(Item(start=start, end=len(lines), types=ItemType.Function, text=text))
        elif state == State.FindDocstring:
            ret.append(Item(start=start, end=len(lines), types=ItemType.Docstring, text=text))

    return ret


def analysis_function(items):
    for item in items:
        info = {}
        if item.types == ItemType.Function:
            # 配置参数列表
            s = item.text
            s = s.strip()
            if s.startswith("class"):
                continue
            s = re.sub(r'#.*\n', "", s)
            st = s.find('(')
            ed = s.find(')')
            if st == -1 or ed == -1:
                continue
            s = s[st + 1:ed]
            if s == '':
                continue
            params = s.split(',')
            for param in params:
                param = param.strip()
                if param == "self":
                    continue
                if param.count("=") != 0:
                    pos = param.find("=")
                    info.setdefault('params', {})
                    if param.count(": ") != 0:
                        mpos = param.find(": ")
                        info['params'].setdefault(param[:mpos].strip(), {})
                        info['params'][param[:pos]].setdefault('type', param[mpos + 1:pos].strip())
                    else:
                        info['params'].setdefault(param[:pos].strip(), {})
                    info['params'][param[:pos]].setdefault('default', param[pos + 1:].strip())
                elif param.count(": ") != 0:
                    pos = param.find(": ")
                    info.setdefault('params', {})
                    info['params'].setdefault(param[:pos].strip(), {})
                    info['params'][param[:pos]].setdefault('type', param[pos + 1:].strip())
                else:
                    info.setdefault('params', {})
                    info['params'].setdefault(param, {})
            # 配置返回值类型
            s = item.text
            s = s.strip()
            if s.startswith("class"):
                continue
            s = re.sub(r'#.*\n', "", s)
            pos = s.find('->')
            if pos != -1:
                s = s[pos + 2:]
                s = s.strip(": \n()")
                if s.count(',') == 0:
                    info.setdefault('rtypeHint', [])
                    info['rtypeHint'].append(s)
                else:
                    rtypes = s.split(',')
                    for rtype in rtypes:
                        one_rtype = rtype.strip()
                        info.setdefault('rtypeHint', [])
                        info['rtypeHint'].append(one_rtype)
            item.info = info
            info = {}
    return items


def analysis_rest(docstring):
    assert type(docstring) == Item
    s = docstring.text
    s = s.strip(docstring.info["lim"] + " \n")
    lines = s.split("\n")
    statement = ""
    now = "statement"
    info = {}
    first_line = "true"
    for line in lines:
        s = line.strip()
        if first_line == "true":
            first_line = "false"
            if s == "":
                continue
            docstring.info.setdefault("summary", s)
            continue
        if s.startswith(":"):
            statement = statement.strip(" ")
            if now == "statement":
                if statement != "":
                    docstring.info.setdefault(now, statement)
                    statement = ""
                now = ""
            else:
                docstring.info.setdefault("contains", [])
                docstring.info["contains"].append({"type": now})
                for k in info:
                    docstring.info["contains"][-1][k] = info[k]
                docstring.info["contains"][-1]["statement"] = statement
                now = ""
                statement = ""
            info = {}
            # s1: 分离statement
            s1 = s[1:]
            # s2: 使用:进行划分
            s2 = s1.split(":")
            key = ""
            name = ""
            p_type = ""
            if len(s2[0].split(" ")) == 1:
                key = s2[0]
            else:
                s3 = s2[0].split(" ")
                key = s3[0]
                name = s3[1]
            pos = s1.find(":")
            s1 = s1[pos + 1:]
            if len(s2) >= 3 and len(s2[1].strip().split(" ")) == 1:
                p_type = s2[1].strip()
                pos = s1.find(":")
                s1 = s1[pos + 1:]
            now = key
            if name != "":
                info["name"] = name
            if p_type != "":
                info["p_type"] = p_type
            statement = s1
        else:
            statement += line + "\n"
    statement = statement.strip(" ")
    if now == "statement":
        docstring.info.setdefault(now, statement)
        statement = ""
        now = ""
    else:
        docstring.info.setdefault("contains", [])
        docstring.info["contains"].append({"type": now})
        for k in info:
            docstring.info["contains"][-1][k] = info[k]
        docstring.info["contains"][-1]["statement"] = statement
        now = ""
        statement = ""
    return docstring


def analysis_epytext(docstring):
    assert type(docstring) == Item
    s = docstring.text
    s = s.strip(docstring.info["lim"] + " \n")
    lines = s.split("\n")
    statement = ""
    now = "statement"
    info = {}
    first_line = "true"
    for line in lines:
        s = line.strip()
        if first_line == "true":
            first_line = "false"
            if s == "":
                continue
            docstring.info.setdefault("summary", s)
            continue
        if s.startswith("@"):
            statement = statement.strip(" ")
            if now == "statement":
                if statement != "":
                    docstring.info.setdefault(now, statement)
                    statement = ""
                now = ""
            else:
                docstring.info.setdefault("contains", [])
                docstring.info["contains"].append({"type": now})
                for k in info:
                    docstring.info["contains"][-1][k] = info[k]
                docstring.info["contains"][-1]["statement"] = statement
                now = ""
                statement = ""
            info = {}
            # s1: 分离statement
            s1 = s[1:]
            # s2: 使用:进行划分
            s2 = s1.split(":")
            key = ""
            name = ""
            p_type = ""
            if len(s2[0].split(" ")) == 1:
                key = s2[0]
            else:
                s3 = s2[0].split(" ")
                key = s3[0]
                name = s3[1]
            pos = s1.find(":")
            s1 = s1[pos + 1:]
            if len(s2) >= 3 and len(s2[1].strip().split(" ")) == 1:
                p_type = s2[1].strip()
                pos = s1.find(":")
                s1 = s1[pos + 1:]
            now = key
            if name != "":
                info["name"] = name
            if p_type != "":
                info["p_type"] = p_type
            statement = s1
        else:
            statement += line + "\n"
    statement = statement.strip(" ")
    if now == "statement":
        docstring.info.setdefault(now, statement)
        statement = ""
        now = ""
    else:
        docstring.info.setdefault("contains", [])
        docstring.info["contains"].append({"type": now})
        for k in info:
            docstring.info["contains"][-1][k] = info[k]
        docstring.info["contains"][-1]["statement"] = statement
        now = ""
        statement = ""
    return docstring


def get_space(line: str) -> int:
    ret = 0
    s = line
    while len(s) > 0 and s[0] == " ":
        ret += 1
        s = s[1:]
    return ret


google_headers = {
    "Args": "param",
    "Arg": "param",
    "Returns": "return",
    "Return": "return",
    "Yields": "yield",
    "Yield": "yield",
    "Raises": "raise",
    "Raise": "raise",

    "Example": "example",
    "Examples": "example",
    "Note": "note",
    "Notes": "note",

    "Attributes": "attribute",
    "Attribute": "attribute",
}


def analysis_google(docstring):
    header_set = {
        "Args:",
        "Returns:",
        "Yields:",
        "Raises:",
        "Arg:",
        "Return:",
        "Yield:",
        "Raise:",

        "Example:",
        "Examples:",
        "Note:",
        "Notes:",

        "Attributes:",
        "Attribute:",
    }
    assert type(docstring) == Item
    s = docstring.text
    spacef = get_space(s)
    spacep = 0
    s = s.strip(docstring.info["lim"] + " \n")
    lines = s.split("\n")
    statement = ""
    now = "statement"
    info = {}
    first_line = "true"
    header_type = ""
    next_header = "false"
    for line in lines:
        s = line
        if first_line == "true":
            first_line = "false"
            if s == "":
                continue
            docstring.info.setdefault("summary", s)
            continue
        if s.strip() in header_set and spacef == get_space(s):
            next_header = "true"
            s = s.strip()[:-1]
            header_type = google_headers[s]
            statement = statement.strip(" ")
            if now == "statement":
                if statement != "":
                    docstring.info.setdefault(now, statement)
                    statement = ""
                now = ""
            else:
                docstring.info.setdefault("contains", [])
                docstring.info["contains"].append({"type": now})
                for k in info:
                    docstring.info["contains"][-1][k] = info[k]
                docstring.info["contains"][-1]["statement"] = statement
                now = ""
                statement = ""
            now = header_type
            info = {}

        elif header_type in {"example", "note"}:  # statement
            statement += line + "\n"

        elif header_type == "return" or header_type == "yield":  # type:statement
            if next_header == "true":
                next_header = "false"
                info = {}
                s = s.strip()
                if s.find(": "):
                    s1 = s[:s.find(": ")].strip()
                    next_header = "false"
                    docstring.info.setdefault("contains", [])
                    docstring.info["contains"].append({"type": "rtype"})
                    docstring.info["contains"][-1]["statement"] = s1
                    now = {"return": "returns", "yield": "yields"}[header_type]
                    statement += s[s.find(": ") + 2:] + "\n"
                else:
                    statement += s + "\n"
            else:
                statement += line + "\n"

        elif header_type != "" and s.find(":") != -1 and (spacep == 0 or spacep == get_space(s)) and (
                (len(s[:s.find(":")].strip()) != 0 and s[:s.find(":")].strip().count(" ") == 0) or (
                len(s[:s.find(":")].strip()) != 0 and s[:s.find(":")].strip().count("(") != 0 and
                s[:s[:s.find(":")].strip().find("(")].strip().count(" ") != 0)):  # name(:type):statement
            if next_header != "true":
                statement = statement.strip(" ")
                docstring.info.setdefault("contains", [])
                docstring.info["contains"].append({"type": now})
                for k in info:
                    docstring.info["contains"][-1][k] = info[k]
                docstring.info["contains"][-1]["statement"] = statement
                now = ""
                statement = ""

            info = {}
            s = s.strip()
            s1 = s[:s.find(": ")].strip()
            s2 = s[s.find(": ") + 2:].strip()
            name = ""
            p_type = ""
            if s1.find("(") != -1:
                name = s1[:s1.find("(")].strtp()
                p_type = s1[s1.find("(") + 1:s1.rfind(")")].strip()
            elif s2[:s2.find(": ")].strip().count(" ") == 0:
                name = s1
                p_type = s2[:s2.find(": ")].strip()
                s2 = s2[s2.find(": ") + 2:]
            else:
                name = s1
            if header_type == "param" or header_type == "attribute":
                info["name"] = name
                if p_type != "":
                    info["p_type"] = p_type
                now = header_type
            # elif header_type == "return":
            #     docstring.info.setdefault("contains", [])
            #     docstring.info["contains"].append({"type": "rtype"})
            #     docstring.info["contains"][-1]["statement"] = s1
            #     now = "returns"
            # elif header_type == "yield":
            #     now = "yield"
            elif header_type == "raise":
                info["name"] = name
                now = "raises"
            statement = s2
            next_header = "false"
        else:
            statement += line + "\n"
    statement = statement.strip(" ")
    if now == "statement":
        if statement != "":
            docstring.info.setdefault(now, statement)
            statement = ""
        now = ""
    else:
        docstring.info.setdefault("contains", [])
        docstring.info["contains"].append({"type": now})
        for k in info:
            docstring.info["contains"][-1][k] = info[k]
        docstring.info["contains"][-1]["statement"] = statement
        now = ""
        statement = ""
    return docstring


def judge_docstring(docstring) -> str:
    lines = docstring.text.split("\n")
    rest = 0
    epytext = 0
    google = 0
    for i in lines:
        s = i.strip(" \n")
        if s == "":
            continue
        if s[0] == ":":
            rest += 1
        if s[0] == "@":
            epytext += 1
        if s[:-1] in google_headers:
            google += 1
    if max(rest, epytext, google) == rest:
        return "reST"
    elif max(rest, epytext, google) == epytext:
        return "Epytext"
    elif max(rest, epytext, google) == google:
        return "Google"
    return "reST"


style_func = {"reST": analysis_rest, "Epytext": analysis_epytext, "Google": analysis_google}


def merge_info(info1, info2):
    ret = {}
    for k in info1:
        ret[k] = info1[k]
    for k in info2:
        ret[k] = info2[k]
    return ret


def analysis_docstring(items):
    for i, item in enumerate(items):
        if items[i].types == ItemType.Docstring and i > 0 and items[i - 1].types == ItemType.Function:
            item.info = merge_info(item.info, items[i - 1].info)
            style = judge_docstring(item)
            item = style_func[style](item)
    return items


def parser_format(items):
    # TODO 转换
    return items


# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    print_hi('PyCharm')
    res = split_lines("./main.py")
    res = analysis_function(res)
    res = analysis_docstring(res)
    '''
    SORRY FOR MY POOR ENGLISH
    
    res : list of Item
    
    class Item:
        def __init__(self, start=0, end=0, types=ItemType.Normal, text="", info={}):
            self.types = types
            self.start = start
            self.end = end
            self.text = text
            self.info = info
            
    types: type of item
        class ItemType(Enum):
            Function = 0            class or function
            Docstring = 1           docstring means all comment with multiline, maybe not real docstring. 
                                    a Docstring is a docstring only when it's after function
            Normal = 2              just normal code
    start: start line of item
    end: end line of item
    text: raw text of item
    info: other infos
        for Function:
            params: map of params
                key: param name
                value: map of other info
                    key: "default" if has default value
                    value: default value of param
            rtypeHint: list of return type hint
        for docstring:
            all info of it's function (params/rtypeHint)
            lim: it's quotation marks type ( ' ' ' or " " ")
            summary: summary if it has summary(all " " and "\n" at front and back will be removed)
            statement:  Description if it has description(all " " and "\n" at front and back will be removed,
                        others will be kept)
            contains: list of other item
                type: (param/return/raise or others)
                name: it's name. like param name / return name / raise name or others
                p_type: it's type(if it has a type)
                statement:  Description if it has description(all " " and "\n" at front and back will be removed, 
                            others will be kept)
                
    '''
    res = parser_format(res)
    print(res)


# 以下是测试用例

def func_epytext(param1: int, param2='default val') -> bool:
    """This is an example function with docstrings in Epytext(javadoc-like) style.

    @param param1: int: This is the first parameter.
    @param param2: This is the second parameter. (Default value = 'default val')
    @return: The return value. True for success, False otherwise.
    @rtype: bool
    @raise keyError: raises key exception
    @raise TypeError: raises type exception

    """
    pass


def func_rest(param1: int, param2='default val') -> bool:
    """This is an example function with docstrings in reST style.

    Life can be good,
    Life can be bad,
    Life can mostly cheerful,
    But sometimes sad.

    :param param1: int: This is the first parameter.
    :param param2: This is the second parameter. (Default value = 'default val')
    :returns: The return value. True for success, False otherwise.
    :rtype: bool
    :raises keyError: raises key exception
    :raises TypeError: raises type exception

    """
    pass


def func_google(param1: int, param2='default val') -> bool:
    """This is an example function with docstrings in Google style.

    Args:
      param1: int: This is the first parameter.
      param2: This is the second parameter. (Default value = 'default val')

    Returns:
      bool: The return value. True for success, False otherwise.

    Raises:
      keyError: raises key exception
      TypeError: raises type exception

    Note:
      This is a note
    """
    pass
