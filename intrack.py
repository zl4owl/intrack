import sys
from typing import List, Optional

from src.interface import run_cli, run_console
from src.gui import run_gui


# Dispatches to CLI or interactive console based on args
def main(argv: Optional[List[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if "--no-gui" in args:
        filtered = [arg for arg in args if arg != "--no-gui"]
        if not filtered:
            return run_console()
        return run_cli(filtered)
    if args:
        return run_cli(args)
    return run_gui()


# Script entry point
if __name__ == "__main__":
    raise SystemExit(main())
