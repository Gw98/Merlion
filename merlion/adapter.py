from format import *
from parser import Item, ItemType

class Adapter(object):
    def __init__(self):
        self.docstrings = []

    
    def adapter(self, items):
        for item in items:
            docstring = self.generate_docstring(item)
            if docstring:
                self.docstrings.append(docstring)


    def generate_docstring(self, item):
        """[summary]

        Args:
            item ([type]): [description]
        """
        if isinstance(item, Item):
            item = item.__dict__
        start = item.get('start', 0)
        end = item.get('end', 0)
        indentation = item.get('indentation', 0)

        type = item.get('types')
        if type != ItemType.Docstring:
            return None

        info = item.get('info')
        summary  = info.get('summary')
        description = info.get('description')
        elements = info.get('contains', [])
        docstring = Docstring(start, end, int(indentation/4), summary, description)    # TODO

        for element in elements:
            generate_func = getattr(self, 'generate_{}'.format(element.get('type')), None)
            if generate_func:
                docstring.elements.append(generate_func(element))

        return docstring


    def generate_param(self, element):
        ele = DocstringElement(DocstringElementType.Param)
        ele.content = DocstringParam(element.get('name'), element.get('p_type'), description=element.get('statement'))
        return ele


    def generate_return(self, element):
        ele = DocstringElement(DocstringElementType.Return)
        ele.content = DocstringReturn(description=element.get('statement'))
        return ele


    def generate_raise(self, element):
        ele = DocstringElement(DocstringElementType.Raise)
        ele.content = DocstringRaise(element.get('name'), element.get('statement'))
        return ele


    def generate_note(self, element):
        ele = DocstringElement(DocstringElementType.Note)
        ele.content = DocstringOther(element.get('name'), single_description=element.get('statement'))
        return ele


# (param/return/raise/yield/example/note/attribute or others)
