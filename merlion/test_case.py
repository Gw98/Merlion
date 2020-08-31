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