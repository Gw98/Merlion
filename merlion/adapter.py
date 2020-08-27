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

        Input:
            {
                'start': 0,
                'end': 0,
                'info': {
                    'summary': 'summary',
                    'description': 'description',
                    'contains': [
                        'type': 'param/return/raise or others',
                        'name': 'name',
                        'p_type': 'type',
                        'statement': 'statement'
                    ]
                },
            }
        """
        if isinstance(item, Item):
            item = item.__dict__
        start = item.get('start', 0)
        end = item.get('end', 0)

        type = item.get('types')
        if type != ItemType.Docstring:
            return None

        info = item.get('info')
        summary  = info.get('summary')
        description = info.get('description')
        elements = info.get('contains', [])
        docstring = Docstring(start, end, 0, summary, description)    # TODO

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


metadata = {
   "end":623,
   "info":{
      "contains":[
         {
            "name":"param1",
            "p_type":"int",
            "statement":"This is the first parameter.",
            "type":"param"
         },
         {
            "name":"param2",
            "statement":"This is the second parameter. (Default ""value = 'default val')",
            "type":"param"
         },
         {
            "statement":"The return value. True for success, ""False otherwise.",
            "type":"return"
         },
         {
            "statement":"bool",
            "type":"rtype"
         },
         {
            "name":"keyError",
            "statement":"raises key exception",
            "type":"raise"
         },
         {
            "name":"TypeError",
            "statement":"raises type exception",
            "type":"raise"
         }
      ],
      "params":{
         "param1":{
            "type":"int"
         },
         "param2":{
            "default":"'default val'"
         }
      },
      "rtypeHint":[
         "bool"
      ],
      "statement":"\n",
      "summary":"This is an example function with docstrings in ""Epytext(javadoc-like) style."
   },
   "start":614,
}


# (Pdb) pp docstring.__dict__
# {'description': None,
#  'elements': [<format.DocstringElement object at 0x10feb3fd0>,
#               <format.DocstringElement object at 0x10feb3950>,
#               <format.DocstringElement object at 0x11050ec10>,
#               <format.DocstringRaise object at 0x11050ed10>,
#               <format.DocstringRaise object at 0x11050ecd0>],
#  'end_line': 623,
#  'start_line': 614,
#  'summary': 'This is an example function with docstrings in '
#             'Epytext(javadoc-like) style.',
#  'tab_cnt': 0}

def main():
    adpt = Adapter()
    adpt.adapter([metadata])


if __name__ == "__main__":
    main()
