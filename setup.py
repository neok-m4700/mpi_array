#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import sys
import subprocess


def read_readme():
    """
    Reads part of the README.rst for use as long_description in setup().
    """
    text = open("README.rst", "rt").read()
    text_lines = text.split("\n")
    ld_i_beg = 0
    while text_lines[ld_i_beg].find("start long description") < 0:
        ld_i_beg += 1
    ld_i_beg += 1
    ld_i_end = ld_i_beg
    while text_lines[ld_i_end].find("end long description") < 0:
        ld_i_end += 1

    ld_text = "\n".join(text_lines[ld_i_beg:ld_i_end])

    return ld_text


def create_git_describe():
    try:
        cmd = ["git", "describe"]
        p = \
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        p.wait()
        if p.returncode != 0:
            e = \
                subprocess.CalledProcessError(
                    returncode=p.returncode,
                    cmd=cmd
                )
            setattr(e, "output", " ".join([i.decode() for i in p.communicate()]))

            raise e
        # Write the git describe to text file
        open(os.path.join("mpi_array", "git_describe.txt"), "wt").write(p.communicate()[0].decode())
    except (Exception,) as e:
        # Try and make up a git-describe like string.
        print("Problem with '%s': %s: %s" % (" ".join(cmd), e, e.output))
        version_str = open(os.path.join("mpi_array", "version.txt"), "rt").read().strip()
        if ("TRAVIS_TAG" in os.environ.keys()) and (len(os.environ["TRAVIS_TAG"]) > 0):
            version_str = os.environ["TRAVIS_TAG"]
        else:
            if ("TRAVIS_BRANCH" in os.environ.keys()) and (len(os.environ["TRAVIS_BRANCH"]) > 0):
                version_str += os.environ["TRAVIS_BRANCH"]
            if ("TRAVIS_COMMIT" in os.environ.keys()) and (len(os.environ["TRAVIS_COMMIT"]) > 0):
                version_str += "-" + \
                    os.environ["TRAVIS_COMMIT"][0:min([7, len(os.environ["TRAVIS_COMMIT"])])]
        open(os.path.join("mpi_array", "git_describe.txt"), "wt").write(version_str)

create_git_describe()

_long_description = read_readme()

mpi4py_requires = ["mpi4py>=2.0", ]
mock_requires = []

if "READTHEDOCS" in os.environ.keys():
    # Skip mpi4py dependency, can't install an MPI implementation
    # in readthedocs.org virtual machine.
    mpi4py_requires = []
    if sys.version_info < (3,3,0):
        mock_requires = ["mock"]

other_requires = mpi4py_requires + mock_requires

sphinx_requires = []

# Only require sphinx for CI and readthedocs.org. 
if (
    (os.environ.get('READTHEDOCS', None) is not None)
    or
    (os.environ.get('CI', None) is not None)
    or
    (os.environ.get('TRAVIS', None) is not None)
    or
    (os.environ.get('APPVEYOR', None) is not None)
):
    sphinx_requires = ["sphinx>=1.4,<1.6", "sphinx_rtd_theme", ]

if (
    (int(sys.version_info[0]) < 2)
    or
    ((int(sys.version_info[0]) == 2) and (int(sys.version_info[1]) <= 6))
    or
    ((int(sys.version_info[0]) == 3) and (int(sys.version_info[1]) <= 3))
):
    sphinx_requires = []

setup(
    name="mpi_array",
    version=open("mpi_array/version.txt", "rt").read().strip(),
    packages=find_packages(),
    # metadata for upload to PyPI
    author="Shane J. Latham",
    author_email="mpi.array@gmail.com",
    description=(
        "Python package providing PGAS multi-dimensional array with numpy-like API."
    ),
    long_description=_long_description,
    license="MIT",
    keywords=(
        "MPI mpi4py data-parallelism distributed numpy ndarray distributed-array"
        +
        " distributed-ndarray scipy domain-decomposition array-decomposition"
    ),
    url="http://github.com/mpi-array/mpi_array",   # project home page
    classifiers=[
        # How mature is this project? Common values are
        #   2 - Pre-Alpha
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ],
    install_requires= \
        [
            "numpy>=1.13.0",
            "array_split>=0.4.0",
            "psutil>=4.3.0",
        ]
        + sphinx_requires
        + other_requires,
    package_data={
        "mpi_array": ["version.txt", "git_describe.txt", "copyright.txt", "license.txt"]
    },
    test_suite="mpi_array.tests",
    scripts=[os.path.join("utils", "mpi_array_info.py"),]
    # could also include download_url, etc.
)
