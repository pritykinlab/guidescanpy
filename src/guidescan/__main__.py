import sys
import guidescan
from guidescan.flask import create_app


commands = (
    'web',
)


def print_usage():
    print('Guidescan v' + guidescan.__version__)
    print('Usage: guidescan <command> <arguments ..>')
    print('\nThe following commands are supported:\n ' + '\n '.join(commands))


def web(*args, **kwargs):
    app = create_app()
    return app.run()


def main():

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in commands:
        print_usage()
        sys.exit(1)

    command = command.replace('-', '_')
    globals()[command](args)


if __name__ == '__main__':
    sys.exit(main())