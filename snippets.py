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

def catalog():
    """
    Retrieves all keywords available.
    If there are no keywords, returns '404 No Snippets Available'
    """
    logging.info("Retrieving all snippets.")
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets order by keyword")
        keywords = cursor.fetchall()
    if not keywords:
        return "404 No Snippets Found"
    logging.debug("Retrieved all snippet keywords successfully")
    return keywords

def search(string):
    """
    Retrieves messages containing search string.
    If there are no keywords, returns '404 No Matching Snippets Found'
    """
    logging.info("Searching for snippet containing search string")
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where message like '%{0}%'".format(string))
        rows = cursor.fetchall()
    if not rows:
        return '404 No Matching Snippets Found Containing', string
    logging.debug("Retrieved matching snippets successfully")
    return rows

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
    logging.debug("Constructing get subparser.")
    get_parser = subparsers.add_parser("get", help="Retrieve a stored snippet")
    get_parser.add_argument("name", help="Name of the snippet")

    #Subparser for the post command
    logging.debug("Constructing post subparser.")
    post_parser = subparsers.add_parser("post", help="Modify a stored snippet")
    post_parser.add_argument("name", help="Name of snippet to update")
    post_parser.add_argument("snippet", help="Updated snippet text")

    #Subparser for delete command
    logging.debug("Constructing delete subparser.")
    delete_parser = subparsers.add_parser("delete", help="Delete a stored snippet")
    delete_parser.add_argument("name", help="Name of snippet to delete")

    #Subparser for catalog command
    logging.debug("Constructing catalog subparser.")
    catalog_parser = subparsers.add_parser("catalog", help="Retrieve all available keywords")

    #Subparser for search command
    logging.debug("Constructing search command.")
    search_parser = subparsers.add_parser("search", help="Retrieve all keywords matching provided search string")
    search_parser.add_argument("string", help="String to find in existing messages")

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
    elif command == "catalog":
        keywords = catalog()
        if keywords == "404 No Snippets Found":
            print("{}".format(keywords))
        else:
            print("Keywords: ")
            for keyword in keywords:
                print(keyword[0])
    elif command == "search":
        string = search(**arguments)
        if "404 No Matching Snippets Found Containing" in string:
            print("{!r}: {!r}".format(string[0], string[1]))
        else:
            print("Matching snippets: ")
            for kw, msg in string:
                print("{!r}: {!r}".format(kw, msg))

if __name__ == "__main__":
    main()
