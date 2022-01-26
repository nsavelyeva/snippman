#!flask/bin/python
import socket
import argparse
from app import app


parser = argparse.ArgumentParser(description="Start SnippMan app.")

parser.add_argument("-s", "--server", default=["0.0.0.0"], nargs=1,
                    help="IP address of a network interface for SnippMan to run on.",
                    required=False)
parser.add_argument("-p", "--port", default=[80], type=int, nargs=1,
                    help="a port number for SnippMan to listen on.",
                    required=False)
parser.add_argument("-v", "--verbose", default=False, type=bool, nargs=1,
                    help="verbose mode, debug messages will be displayed.",
                    required=False)

args = vars(parser.parse_args())


try:
    app.run(host=args["server"][0], port=args["port"][0], debug=args["verbose"])
except OSError as err:
    print("Cannot start SnippMan app due to OS error:\n\t%s." % err)
    print("Is the port %s already in use?" % args["port"][0])
    print("Try 'run.py -h' to see launching options.")
except socket.gaierror as err:
    print("Cannot start SnippMan app due to socket error:\n\t%s." % err)
    print("Is the network interface %s correct?" % args["server"][0])
    print("Try 'run.py -h' to see launching options.")
