"""
A setuptools based setup module for Piecewise constant signal recovery package
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

pkg_info = {}

with open("pymcuexplorer/package_info.py") as fp:
    exec(fp.read(), pkg_info)

setup(
    name="pymcuexplorer",
    version=pkg_info["__version__"],
    description="Python module for exploring Cortex-M MCU memory and peripherals on PC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ngmikheev/pymcuexplorer",
    author=pkg_info["__version__"],
    author_email=pkg_info["__email__"],
    keywords="mcu, debug, registers, memory, svd, pyocd, cortex, IAR",
    package_dir={"": "pymcuexplorer"},
    packages=find_packages(where=""),
    python_requires=">=3.6, <4",
    install_requires=["pyocd"],
    extras_require={
        "dev": ["jupyter"],
        "test": ["pytest", "pytest-cov"],
    },
)
