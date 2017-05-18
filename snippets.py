import logging
import argparse
import psycopg2

#Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to postgres")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def put(name, snippet):
    """
    Stores a snippet with an associated name.
    Returns the name and the snippet.
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    cursor = connection.cursor()
    try:
        command = "insert into snippets values (%s, %s)"
        cursor.execute(command, (name, snippet))
        connection.commit()
        logging.debug("Snippet stored successfully.")
    except psycopg2.IntegrityError as e:
        connection.rollback()
        command = "update snippets set message=%s where keyword=%s"
        cursor.execute(command, (snippet, name))
        connection.commit()
    return name, snippet

def get(name):
    """
    Retrieve the snippet with the given name.
    If there is no such snippet, return '404 Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Getting snippet {!r}".format(name))
    cursor = connection.cursor()
    command = "select message from snippets where keyword=%s"
    cursor.execute(command, (name,))
    row = cursor.fetchone()
    connection.commit()
    if not row:
        return "404 Snippet Not Found"
    logging.debug("Snippet retrieved successfully.")
    return row[0]

def post(name, snippet):
    """
    Retrieve snippet with the given name.
    If there is no such snippet, return '404 Snippet Not Found'.
    Modify the snippet by replacing the current snippet with the one provided.
    Returns the name and the snippet.
    """
    logging.error("FIXME - Unimplemented - post{!r}, {!r}".format(name, snippet))
    #Think about error handling here in case get fails - raise exception with message
    return name, snippet

def delete(name):
    """
    Delete snippet with the given name.
    If there is no such snippet, return '404 Snippet Not Found'.
    Returns the name of the deleted snippet.
    """
    logging.error("FIXME - Unimplemented - delete{!r}".format(name))
    #Think about error handling here in case get fails - raise exception with message
    return ""

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text.")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    #Subparser for the put command
    logging.debug("Constructing put subparser.")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")

    #Subparser for the get command
    logging.debug("Constructing the get subparser.")
    get_parser = subparsers.add_parser("get", help="Retrieve a stored snippet")
    get_parser.add_argument("name", help="Name of the snippet")

    arguments = parser.parse_args()

    #Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))

if __name__ == "__main__":
    main()
