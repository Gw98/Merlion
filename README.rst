=======
Merlion
=======

A Python Docstring Style Converter(Reformatter)

.. contents:: :local:

Description
-----------

Merlion can help you convert Python docstring from one style to another in existing Python files.

People may want to reformat the docstrings in program when:

- Teamworking (need unified docstring style)
- Reviewing others’ code (prefer familiar docstring style)
- ...

Merlion will parse one or several Python scripts and then retrieve the existing docstring. For all found functions/methods/classes with an existing docstring, it will fetch their parameters, default values, type, ... Then Merlion will generate new formatted docstring from the existing docstring content and the factors it found.

After that, patches will be generated for each file, for the users to apply the patches to the initial scripts.

Features
--------

* Supported input docstring style: Google, reST, Epytext
* Supported output docstring style: Google, Numpydoc, reST, Epytext

Usage
-----

- install from Pypi

TODOs

Example
-------


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
