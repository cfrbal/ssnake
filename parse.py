import argparse

parser = argparse.ArgumentParser(
                    prog='SSnake',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('user:prompt')           # positional argument
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()
print(args.verbose)