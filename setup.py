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
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
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
    name="hyo2.soundspeed",
    version=find_version("hyo2", "soundspeed", "__init__.py"),
    license='LGPLv2.1 or CCOM-UNH Industrial Associate license',

    namespace_packages=[
        "hyo2"
    ],
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests", "*.test*",
    ]),
    package_data={
        "": [
            'soundspeed/listener/seacat/CONFIG/*.*',
            'soundspeedmanager/media/*.*',
            'soundspeedmanager/media/LICENSE',
            'soundspeedsettings/media/*.*',
        ],
    },
    zip_safe=False,
    setup_requires=[
        "setuptools",
        "wheel",
        "coverage"
    ],
    install_requires=[
        "hyo2.abc",
        "gsw",
        "netCDF4",
        "pillow",
        "pyserial",
        "requests",
        "scipy"
    ],
    python_requires='>=3.5',
    entry_points={
        "gui_scripts": [
            'sound_speed_manager = hyo2.soundspeedmanager.gui:gui',
            'sound_speed_settings = hyo2.soundspeedsettings.gui:gui',
        ],
        "console_scripts": [
        ],
    },
    test_suite="tests",

    description="A library and an application to manage sound speed profiles.",
    long_description=(read("README.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("HISTORY.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("AUTHORS.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read(os.path.join("docs", "developer_guide_how_to_contribute.rst")))
    ,
    url="https://github.com/hydroffice/hyo2_soundspeed",
    classifiers=[  #
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Office/Business :: Office Suites',
    ],
    keywords="hydrography ocean mapping survey sound speed profiles",
    author="Giuseppe Masetti(UNH,CCOM); Barry Gallagher(NOAA,OCS); " \
           "Chen Zhang(NOAA,OCS); Matthew Sharr (NOAA,OCS)",
    author_email="gmasetti@ccom.unh.edu, barry.gallagher@noaa.gov, " \
                 "chen.zhang@noaa.gov, matthew.sharr@noaa.gov",
)
