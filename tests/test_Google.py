from format import *

elem0 = DocstringElement(DocstringElementType.Param)
elem0.content = DocstringParam("param0", "int", "10",
                               "the description of param0,\n                    a lot of space. balabalabalabalabalabblalblablalblalbalblalblablalblalblabllablalabalababalalbalblalblalblallabalabaend")

elem4 = DocstringElement(DocstringElementType.Param)
elem4.content = DocstringParam(param_name="param1", default_value="string",
                               description="the description of param0, it is very long balabalabalabalabalabblalblablalblalbalblalblablalblalblabllablalabalababalalbalblalblalblallabalabaend")

elem5 = DocstringElement(DocstringElementType.Param)
elem5.content = DocstringParam(param_name="test", type_name="",
                               description="it is also very long balabalbabalabalabalabalabalabalabalabalabalababalabalbaballbalblalbalblalblalbalblalblablalblalblallblalbalblalbalbalblalblaend")

elem1 = DocstringElement(DocstringElementType.Return)
elem1.content = DocstringReturn(
    type_name="bool", description="true for success, false for failure")

elem6 = DocstringElement(DocstringElementType.Return)
elem6.content = DocstringReturn(
    description="true for success, false for failure")

elem2 = DocstringElement(DocstringElementType.Raise)
elem2.content = DocstringRaise(
    "IOException", "it is also very long balabalbabalabalabalabalabalabalabalabalabalababalabalbaballbalblalbalblalblalbalblalblablalblalblallblalbalblalbalbalblalblaend")

elem3 = DocstringElement(DocstringElementType.Note)
elem3.content = DocstringOther(
    single_description="PEP 484_ type annotations are supported. If attribute, parameter, and return types are annotated according to PEP 484_, they do not need to be included in the docstring")


docstring1 = Docstring(1, 3, 1)
docstring1.elements = [elem0, elem1, elem2, elem3, elem4, elem5, elem6]


docstring2 = Docstring(6, 8, 1)
docstring2.elements = [elem0, elem1, elem2, elem3, elem4, elem5, elem6]

file = File(input_file_name="test_Google.py", prog=["def func(param0: int = 10, param1 = \"string\") -> bool:\n", "\"\"\"docstring\n", "\"\"\"\n", "pass", "\n", "def func(param0: int = 10, param1 = \"string\") -> bool:\n", "\"\"\"docstring\n", "\"\"\"\n", "pass\n"], quote="\'", docs_list=[
            docstring1, docstring2], target_style=DocstringStyle.Google)

file.format()
