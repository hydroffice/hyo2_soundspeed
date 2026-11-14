import sys

from hyo2.abc2.lib.logging import set_logging

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2", "hyo2.sdm3"])


def main():
    if len(sys.argv) == 1:
        from hyo2.ssm2.app.gui.soundspeedmanager.gui import gui
        gui()
    else:
        from hyo2.ssm2.app.cli.cli import cli
        cli()
