#!/usr/bin/env python

import argparse
import logging
import psycopg2
import sys

# Set the log output file, and the log level

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="The name of the snippet")
    put_parser.add_argument("snippet", help="The snippet text")

    # Subparser for the get command 
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Get a snippet")
    get_parser.add_argument("name", help="The name of the snippet")

    # Subparser for the catalog command 
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Print a catalog of snippet keywords")
    
    # Subparser for the contains command 
    logging.debug("Constructing contains subparser")
    contains_parser = subparsers.add_parser("contains", help="Print a catalog of snippet messages containing a given string")
    contains_parser.add_argument("searchstr", help="The string that should be contained in the snippet messages")
    
    arguments = parser.parse_args(sys.argv[1:])

    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
            name, snippet = put(**arguments)
            print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
            snippet = get(**arguments)
            print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
            catalog()
            print("Retrieved all snippet keywords for user to browse")
    elif command == "contains":
            contains(**arguments)
            print("Retrieved all snippets containing the given string")

def contains(searchstr):
    """
    Display all the snippets containing a given string
    """
    logging.debug("Getting all snippets containing a given string")     
    command = "select message from snippets where message like \'%" + searchstr + "%\'"
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(command)
            rows = cursor.fetchall()
            for row in rows:
                print row[0]
                print "snippet message: %s" % row[0]
            print
    except psycopg2.Error as e:
        print e

def catalog():
    """
    Display a catalog of all snippet keywords 
    for the user to browse through
    """
    logging.debug("Getting all snippet keywords")
    command = "select keyword from snippets order by keyword asc"
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(command)
            rows = cursor.fetchall()
            for row in rows:
                print row[0]
    except psycopg2.Error as e:
        print e
    
def put(name, snippet):
    """
    Store a snippet with an associated name.
    Returns the name and the snippet
    """
    logging.debug("Storing snippet into database {!r} {!r}".format(name, snippet))
    command = "insert into snippets values (%s, %s)"
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(command, (name, snippet))
        logging.debug("Snippet stored successfully.");

    except psycopg2.IntegrityError as e:
        print e
        print "Attempting an update instead"
        command = "update snippets set message = %s where keyword = %s"
        with connection, connection.cursor() as cursor:
             cursor.execute(command, (snippet, name))
        logging.debug("Snippet updated successfully.");
    
    return name, snippet

def get(name):
    """
    Retrieve the snippet with a given name.

    If there is no such snippet return None
    """
    logging.debug("Getting snippet from database {!r}".format(name))
    command = "select message from snippets where keyword = %s"
    with connection, connection.cursor() as cursor:
        cursor.execute(command, (name,))
        row = cursor.fetchone()

    return row[0] if row else None

if __name__ == '__main__':
    logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
    logging.debug("Connecting to PostgreSQL")
    connection = psycopg2.connect("dbname='snippets' user='ubuntu'")
    logging.debug("Database connection established.")
    main()
    connection.close()
