# Community [![Build Status](https://travis-ci.com/jthistle/community.svg?branch=master)](https://travis-ci.com/jthistle/community)
A community simulator written in Python.

[The wiki](https://github.com/jthistle/community/wiki) isn't complete, but contains some information about this project.

Warning: I have not, and likely will not, implement backwards compatability for save files. Every update can and probably will break any save files.

## Install instructions
### Requirements
Python 3 required, 3.6+ recommended.
This program requires the `names` python package and `tkinter`.

Install names through pip with:

	python3 -m pip install names

If tkinter isn't installed, install it.

Ubuntu:
	
	sudo apt-get install python3-tk

Then, just run `main.py` and hey presto, it should work.

Please report any issues found to the tracker.

## Contributing
Contributing is a bit difficult at the moment - this project is in early stages. Any issue marked 'Good First Issue' is one that is considered fixable by first-time contributers, however - so fork and make a pull request! It may be slightly difficult due to the lack of documentation, but if it works, it works, and any useful contributions are very much appreciated.

[pycodestyle](https://pypi.org/project/pycodestyle/) should be used to lint any contributions before opening a pull request. Installation:

	pip install pycodestyle
