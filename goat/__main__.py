"""Entry point so `python -m goat` works."""

from .cli import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
