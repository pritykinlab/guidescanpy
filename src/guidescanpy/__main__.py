import sys
import guidescanpy
from guidescanpy.flask import create_app


commands = ("web",)


def print_usage():
    print("Guidescanpy v" + guidescanpy.__version__)
    print("Usage: guidescanpy <command> <arguments ..>")
    print("\nThe following commands are supported:\n " + "\n ".join(commands))


def web(args):
    app = create_app()
    return app.run(host="0.0.0.0", port=5001, debug=True)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in commands:
        print_usage()
        sys.exit(1)

    command = command.replace("-", "_")
    globals()[command](args)


if __name__ == "__main__":
    sys.exit(main())
