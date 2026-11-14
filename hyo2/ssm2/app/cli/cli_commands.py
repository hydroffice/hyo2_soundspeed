import argparse

# noinspection PyUnresolvedReferences
from hyo2.ssm2 import __version__
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib import formats


class CliCommands:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument('--version', action='version', version=__version__)
        self.subparsers = self.parser.add_subparsers()

        self.converter = self.subparsers.add_parser('convert',
                                                    help='Import, process and export sound speed profiles',
                                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.converter.add_argument('input_path', type=str,
                                    help='The input file or folder.')
        self.converter.add_argument('output_folder', type=str,
                                    help='The output folder for the results of the search.')
        self.converter.add_argument('-s', '--save_to_database', action='store_true', default=False,
                                    help='Enable the saving of the profile to the database.')
        self.converter.add_argument('-r', '--retrieve_temperature_salinity', action='store_true', default=False,
                                    help='Enable the retrieval of temperature/salinity using the atlas selected in the setup.')
        self.converter.add_argument('-x', '--extend_profile', action='store_true', default=False,
                                    help='Enable the profile extension using the atlas selected in the setup.')
        self.converter.add_argument('-i', '--input_format', required=True, type=str,
                                    choices=[e for e in formats.name_readers],
                                    help='The format of the input file')
        self.converter.add_argument('-o', '--output_format', required=True, type=str,
                                    choices=[e for e in formats.name_writers],
                                    help='The format of the output file')


def get_parser() -> argparse.ArgumentParser:
    return CliCommands().parser
