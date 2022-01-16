#!/bin/bash

PY_FILES=$(find . -name '*.py' -print)

for py_file in $PY_FILES; do
  echo $py_file
  autopep8 --in-place --aggressive --aggressive $py_file 
done
