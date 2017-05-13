import logging

#Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

def put(name, snippet):
    """
    Stores a snippet with an associated name.
    Returns the name and the snippet
    """
    logging.error("FIXME: Unimplemented - put{!r}, {!r}".format(name, snippet))
    #Think about error handling here in case get fails - raise exception with message
    return ""

def get(name):
    """
    Retrieve the snippet with the given name.
    If there is no such snippet, return '404 Snippet Not Found'.
    Returns the snippet.
    """
    logging.error("FIXME - Unimplemented - get{!r}".format(name))
    #Think about error handling here in case it fails - raise exception with message
    return ""
