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
    """ 这个函数可以按行
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

            elif l.startswith('def ') or l.startswith('class '):
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
                    info['params'].setdefault(param[:pos], {})
                    info['params'][param[:pos]].setdefault('default', param[pos + 1:])
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


def judge_docstring(docstring) -> str:
    # TODO 配置自动判断docstring类型
    return "reST"


def analysis_rest(docstring):
    assert type(docstring) == Item
    s = docstring.text
    s = s.strip(docstring.info["lim"] + " \n")
    lines = s.split("\n")
    statement = ""
    now = "statement"
    info = {}
    for line in lines:
        s = line.strip()
        if s.startswith(":"):
            statement = statement.strip(" \n")
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
    statement = statement.strip(" \n")
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


style_func = {"reST": analysis_rest}


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
    res = parser_format(res)
    print(res)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
