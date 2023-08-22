#!/bin/bash

docker run --rm -v "$PWD"/demo:/src/demo -v "$PWD"/result:/src/result hiseulgi/license-plate python main.py "$@"