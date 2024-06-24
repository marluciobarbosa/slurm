#!/bin/bash

# pip install pyinstaller
# pyinstaller --onefile --windowed job_generator.py


# pip install cx_Freeze
# python setup.py build


pip install nuitka
python -m nuitka --standalone job_generator.py
