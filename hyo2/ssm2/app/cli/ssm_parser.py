import logging
import os
from urllib.request import urlopen

import numpy as np

# noinspection PyUnresolvedReferences
from hyo2.abc2.app.browser.web_renderer import WebRenderer
# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
# noinspection PyUnresolvedReferences
from hyo2.ssm2 import pkg_info
# noinspection PyUnresolvedReferences
from hyo2.ssm2.app.cli.cli_commands import CliCommands
# noinspection PyUnresolvedReferences
from hyo2.ssm2.app.gui.soundspeedmanager import app_info
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib import formats
from hyo2.ssm2.lib.profile.dicts import Dicts
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class SSMParser:

    def __init__(self) -> None:
        self._check_latest_release()
        self.cli_commands = CliCommands()
        self.cli_commands.converter.set_defaults(func=self.run_converter)
        self._web = None

    def run(self) -> None:
        self._web = WebRenderer(make_app=True)
        args = self.cli_commands.parser.parse_args()
        try:
            args.func(args)
        except AttributeError as e:
            if "'Namespace' object" not in str(e):
                logger.info(e)
            else:
                logger.debug(e, exc_info=True)
            self.cli_commands.parser.print_help()
            self.cli_commands.parser.exit()

    def _check_web_page(self, token: str = "") -> None:
        try:
            if len(token) > 0:
                url = "%s_cli_%s" % (PkgHelper(pkg_info=pkg_info).web_url(), token)
            else:
                url = "%s_cli" % PkgHelper(pkg_info=pkg_info).web_url()
            self._web.open(url=url)
            logger.debug('check %s' % url)

        except Exception as e:
            logger.warning(e)

    @classmethod
    def _check_latest_release(cls) -> None:
        try:
            url = "https://www.hydroffice.org/latest/soundspeed.txt"
            response = urlopen(url, timeout=1)
            latest_version = response.read().split()[0].decode()
            cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
            lat_maj, lat_min, lat_fix = latest_version.split('.')

            if int(lat_maj) > int(cur_maj):
                logger.info("new release available: %s" % latest_version)

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                logger.info("new release available: %s" % latest_version)

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) and (int(lat_fix) > int(cur_fix)):
                logger.info("new bugfix available: %s" % latest_version)

        except Exception as e:
            logger.warning(e)

    def run_converter(self, args):
        if not os.path.exists(args.input_path):
            raise RuntimeError('Unable to locate input path: %s' % args.input_path)
        in_path = args.input_path
        logger.debug('input path: %s' % in_path)

        if not os.path.exists(args.output_folder):
            raise RuntimeError('Unable to locate output folder: %s' % args.output_folder)
        out_folder = args.output_folder
        logger.debug('output folder: %s' % out_folder)

        in_fmt = args.input_format
        in_idx = formats.name_readers.index(in_fmt)
        logger.debug('input format: %s' % in_fmt)
        out_fmt = args.output_format
        logger.debug('output format: %s' % out_fmt)

        save_db = args.save_to_database
        logger.debug('save to database: %s' % save_db)

        temp_sal = args.retrieve_temperature_salinity
        logger.debug('retrieve temperature/salinity: %s' % temp_sal)

        ext_profile = args.extend_profile
        logger.debug('extend profile: %s' % ext_profile)

        skip_atlas = True
        if temp_sal or ext_profile:
            skip_atlas = False

        if os.path.isdir(in_path):
            exts = formats.ext_readers[in_idx]
            logger.debug(f"input format ext: {exts}")
            with os.scandir(in_path) as entries:
                inputs = sorted(
                    entry.path
                    for entry in entries
                    if entry.is_file()
                    and os.path.splitext(entry.name)[1][1:].lower() in exts
                )
        else:
            inputs = [in_path,]
        logger.debug(f"inputs: {inputs}")

        lib = SoundSpeedLibrary()

        for input_file in inputs:
            # import
            lib.import_data(data_path=input_file, data_format=in_fmt, skip_atlas=skip_atlas)

            if temp_sal:
                if lib.cur.meta.sensor_type in [Dicts.sensor_types['XBT'], ]:
                    if not lib.replace_cur_salinity():
                        logger.warning(f"{input_file}: Issue in replacing the salinity")
                        continue

                if lib.cur.meta.sensor_type in [Dicts.sensor_types['XSV'],
                                                     Dicts.sensor_types['SVP']]:
                    if not lib.replace_cur_temp_sal():
                        logger.warning(f"{input_file}: Issue in replacing temperature and salinity")
                        continue
                elif lib.cur.meta.sensor_type in [Dicts.sensor_types['MVP'], ]:

                    if (np.sum(lib.cur.proc.temp) == 0) and (np.sum(lib.cur.proc.sal) == 0):
                        if not lib.replace_cur_temp_sal():
                            logger.warning(f"{input_file}: Issue in replacing temperature and salinity")
                            continue

                if ext_profile and not lib.extend_profile():
                    logger.warning(f"{input_file}: Issue in extending the profile!\n\n"
                          "Possible causes:\n" 
                          "- The extension source is not active. Look at Setup/Input!\n"
                          "- The profile from the extension source is too short. Check it on the plots!\n"
                          "- The extension source does not have a profile at the geographic location.\n"
                          "Use another source or manually extend the profile!")
                    continue

            if save_db:
                lib.store_data()

            lib.export_data(data_formats=[out_fmt,], data_paths={out_fmt: out_folder})
