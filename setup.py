import codecs
import os
import re

from setuptools import setup, find_packages

# ------------------------------------------------------------------
#                         HELPER FUNCTIONS

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(str(os.path.join(here, *parts)), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M, )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


# ------------------------------------------------------------------
#                          POPULATE SETUP

setup(
    name="hyo2.ssm2",
    version=find_version("hyo2", "ssm2", "__init__.py"),
    license='LGPLv2.1 or CCOM-UNH Industrial Associate license',

    namespace_packages=[
        "hyo2"
    ],
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests", "*.test*",
    ]),
    package_data={
        "": [
            'hyo2/ssm2/lib/listener/seacat/CONFIG/*.*',
            'hyo2/ssm2/app/gui/soundspeedmanager/media/*.*',
            'hyo2/ssm2/app/gui/soundspeedmanager/media/LICENSE',
            'hyo2/ssm2/app/gui/soundspeedsettings/media/*.*',
            'hyo2/ssm2/app/gui/ssm_sis/media/*.*'
        ],
    },
    zip_safe=False,
    setup_requires=[
        "setuptools",
        "coverage"
    ],
    install_requires=[
        "hyo2.abc2>=2.4.6",
        "appdirs",
        "cartopy",
        "gsw",
        "matplotlib",
        "netCDF4",
        "numpy<2.0.0",
        "pillow",
        "pyserial",
        "PySide6",
        "requests",
        "scipy",
    ],
    python_requires='>=3.11',
    entry_points={
        "gui_scripts": [
            'sound_speed_manager = hyo2.ssm2.app.gui.soundspeedmanager.gui:gui',
            'sound_speed_settings = hyo2.ssm2.app.gui.soundspeedsettings.gui:gui',
            'ssm_sis = hyo2.ssm2.app.gui.ssm_sis.gui:gui'
        ],
        "console_scripts": [
        ],
    },
    test_suite="tests",

    description="A library and an application to manage sound speed profiles.",
    long_description=(read("README.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("HISTORY.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("AUTHORS.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read(os.path.join("docs", "developer_guide_how_to_contribute.rst"))),
    url="https://github.com/hydroffice/hyo2_soundspeed",
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Office/Business :: Office Suites',
    ],
    keywords="hydrography ocean mapping survey sound speed profiles",
    author="Giuseppe Masetti(UNH,JHC-CCOM); Barry Gallagher(NOAA,OCS); " \
           "Chen Zhang(NOAA,OCS)",
    author_email="gmasetti@ccom.unh.edu, barry.gallagher@noaa.gov, " \
                 "chen.zhang@noaa.gov",
)
