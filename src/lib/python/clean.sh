#!/bin/bash

find ./ -name "*.pyc" -exec rm -i {} \;
find ./ -name "*.py~" -exec rm -i {} \;
