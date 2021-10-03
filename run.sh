#! /bin/bash

if test -f '.venv/scripts/activate'; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

python src/main.py