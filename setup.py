from setuptools import setup, find_packages
import os

# Single-source version information
__version__ = None
__license__ = None
__author__ = None
repo_root = os.path.join(os.path.dirname(__file__))
vers_file = os.path.join(repo_root, "tc2100", "version.py")
exec(open(vers_file).read())

with open('README.md') as readme:
    long_description = readme.read()


with open('requirements.txt') as requirements:
    dependencies = [line.strip() for line in requirements]


setup(
    name='tc2100',
    version=__version__,
    license=__license__,
    description='Receive data from a compatible USB digital thermometer',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author=__author__,
    author_email='3526918+cbs228@users.noreply.github.com',
    url='https://github.com/cbs228/tc2100',

    platforms=['any'],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Framework :: Twisted',
    ],
    keywords='thermometer tc2100 thermocouple 10c4:ea60 serial driver',

    entry_points={
        'console_scripts': ['tc2100dump=tc2100.__main__:main'],
    },

    packages=find_packages(),

    install_requires=dependencies,
)
