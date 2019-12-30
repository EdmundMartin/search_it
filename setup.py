import sys
import pathlib
from setuptools import find_packages
from distutils.core import setup


if sys.version_info <= (3, 5, 3):
    raise RuntimeError("aiohttp 3.x requires Python 3.5.3+")


here = pathlib.Path(__file__).parent


install_requires = [
    'aiohttp>=3.6.2',
    'beautifulsoup4>=4.8.2',
]


def read(f):
    return (here / f).read_text('utf-8').strip()


args = dict(
    name='searchit',
    version='2019.12.30.2',
    description='Aysncio search engine scraping package',
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    author='Edmund Martin',
    maintainer='Edmund Martin <edmartin101@gmail.com>',
    maintainer_email='edmartin101@gmail.com',
    url='https://github.com/EdmundMartin/search_it',
    packages=find_packages(exclude=('tests', '*.tests', '*.tests.*')),
    python_requires='>=3.6',
    install_requires=install_requires,
    include_package_data=True,
)

setup(**args)
