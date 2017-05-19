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
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute("insert into snippets values (%s, %s)", (name, snippet))
            logging.debug("Snippet stored successfully")
        except psycopg2.IntegrityError as e:
            connection.rollback()
            cursor.execute("update snippets set message=%s where keyword=%s", (snippet, name))
            logging.debug("Cannot insert new snippet with keyword duplicate - successfully updated message")
    return name, snippet

def get(name):
    """
    Retrieve the snippet with the given name.
    If there is no such snippet, return '404 Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Getting snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        row = cursor.fetchone()
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
    logging.info("Updating snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        if cursor.fetchone() is not None:
            cursor.execute("update snippets set message=%s where keyword=%s", (snippet, name))
        else:
            return name, "404 Snippet Not Found"
    logging.debug("Snippet updated successfully")
    return name, snippet

def delete(name):
    """
    Delete snippet with the given name.
    If there is no such snippet, return '404 Snippet Not Found'.
    Returns the name of the deleted snippet.
    """
    logging.info("Deleting snippet {!r}".format(name,))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        if cursor.fetchone() is not None:
            cursor.execute("delete from snippets where keyword=%s", (name,))
        else:
            return "404 Snippet Not Found"
    logging.debug("Snippet deleted successfully")
    return name

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

    #Subparser for the post command
    logging.debug("Constructing the post subparser.")
    post_parser = subparsers.add_parser("post", help="Modify a stored snippet")
    post_parser.add_argument("name", help="Name of snippet to update")
    post_parser.add_argument("snippet", help="Updated snippet text")

    #Subparser for delete command
    logging.debug("Constructing the delete subparser.")
    delete_parser = subparsers.add_parser("delete", help="Delete a stored snippet")
    delete_parser.add_argument("name", help="Name of snippet to delete")

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
    elif command == "post":
        name, snippet = post(**arguments)
        print("Updated {!r} to: {!r}".format(name, snippet))
    elif command == "delete":
        name = delete(**arguments)
        print("Deleted snippet: {!r}".format(name))

if __name__ == "__main__":
    main()
