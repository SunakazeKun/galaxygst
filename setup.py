import setuptools
from galaxygst import __version__, __author__

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="galaxygst",
    version=__version__,
    author=__author__,
    url="https://github.com/SunakazeKun/galaxygst",
    description="Python tool to record GST object playback for Super Mario Galaxy 2",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=["nintendo", "super-mario-galaxy-2", "gst", "dolphin", "modding"],
    packages=setuptools.find_packages(),
    install_requires=["dolphin_memory_engine"],
    python_requires=">=3.10",
    license="gpl-3.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only"
    ],
    entry_points={
        "console_scripts": [
            "galaxygst = galaxygst.__main__:main"
        ]
    }
)
