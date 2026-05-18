import sys

from src.interface import run_cli, run_console


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        return run_cli(args)
    return run_console()


if __name__ == "__main__":
    raise SystemExit(main())

