#! /bin/bash

export PYTHON_SYSTEM_RUNTIME=python

$PYTHON_SYSTEM_RUNTIME -m venv .venv

if test -f '.venv/scripts/activate'; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

pip install -r requirements.txt
pip install -e ./src

echo \
'TO_SORT=../to_sort
ROM_ROOT=../rom_root
DAT_ROOT=../dat_root

SS_USERNAME=
SS_PASSWORD=' > .env