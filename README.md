# Satisfactor-Py

A Python utility for planning factories in the video game [Satisfactory](https://www.satisfactorygame.com/). Much information here is taken from the [Satisfactory Wiki](https://satisfactory.fandom.com/wiki/Satisfactory_Wiki).


## Setup

Make a virtual environment, activate it, install dependencies:

```
virtualenv -p python3 .venv
. ./bin/activate
pip install -r requirements.txt
```


## Run Something

Right now, this is all CLI-driven and written up in Python code. A good place to start is the screw factory test script:

```
PYTHONPATH=. ./scripts/screw_factory.py
```