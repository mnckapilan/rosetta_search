from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='rosetta_search',
    url="https://github.com/mnckapilan/rosetta_search",
    author="Kapilan M",
    author_email="mnckapilan+git@gmail.com",
    version='0.0.3',
    description="Semantic Code Search informed by git commit messages",
    packages=find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    package_dir={'': 'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "GitPython~=3.1.14",
        "nltk~=3.6.1",
        "tqdm~=4.60.0"
    ]
)
