import os
from os import path
import json
import shutil as sh
from zipfile import ZipFile
import requests
import zlib
from typing import List


def find_files(path: str) -> list:
  files = []
  
  for root, _, file_names in os.walk(path):
    for file_name in file_names:
      files.append(f'{root}/{file_name}')

  return files


def move_to_tmp(file_path: str) -> List[str]:
  file_ext = file_path.split('.')[-1]

  if file_ext == 'zip':
    with ZipFile(file_path, 'r') as zipfile:
      inner_files = zipfile.filelist

      zipfile.extractall('tmp')

      file_list = []

      for inner_file in inner_files:
        file_list.append(inner_file.filename)

      return(file_list)
  else:
    file_name = path.basename(file_path)

    sh.copy(file_path, 'tmp')

    return [ file_name ]


def crc(filepath) -> str:
  import hashlib

  BUF_SIZE = 65536

  with open(filepath, 'rb') as infile:
    hash = 0
    data = infile.read(BUF_SIZE)

    while data:
      hash = zlib.crc32(data, hash)
      data = infile.read(BUF_SIZE)

    return "%08X" % (hash & 0xFFFFFFFF)


def get_file_info(file_name: str, crc: str):
  request_url = f'https://www.screenscraper.fr/api2/jeuInfos.php?romtype=rom&output=json&crc={crc}&romnom={file_name}'

  response = requests.get(request_url)

  if response.status_code == 200:
    return json.loads(response.text)['response']
  else:
    raise ValueError(f'{response.status_code}: {file_name}: {response.text}')


def get_dest(file_info: dict) -> list:
  game_info = file_info['jeu']

  system_name = game_info['systeme']['text'] if 'systeme' in game_info and 'text' in game_info['systeme'] else 'Unknown'
  publisher = game_info['editeur']['text'] if 'editeur' in game_info and 'text' in game_info['editeur'] else 'Unknown'
  developer = game_info['developpeur']['text'] if 'developpeur' in game_info and 'text' in game_info['developpeur'] else 'Unknown'

  for game_name in game_info['noms']:
    if game_name['region'] == 'ss':
      game_name = game_name['text']
      break

  return [system_name, publisher, developer, game_name]


def create_dir(path: list) -> str:
  if 'sorted' not in os.listdir():
    os.mkdir('sorted')

  path_str = 'sorted'

  for part in path:
    if part not in os.listdir(path_str):
      os.mkdir(f'{path_str}/{part}')

    path_str += f'/{part}'

  return path_str


def sort_file(file_path: str, dest: str, file_crc: str) -> None:
  zip_file = f'{dest}/{file_crc}.zip'

  if not os.path.isfile(zip_file):
    file = ZipFile(zip_file, 'w')
    os.chdir('tmp')
    file.write(file_path.split('/')[-1])
    os.chdir('..')
    file.close()


def ingest_file(file_path: str) -> None:
  if 'tmp' not in os.listdir():
    os.mkdir('tmp')
  
  if 'failed' not in os.listdir():
    os.mkdir('failed')

  file_names = move_to_tmp(file_path)

  for file_name in file_names:
    tmp_file_path = f'tmp/{file_name}'
    file_crc = crc(tmp_file_path)

    try:
      file_info = get_file_info(tmp_file_path, file_crc)
      dest_path = get_dest(file_info)
      sort_path = create_dir(dest_path)
      sort_file(tmp_file_path, sort_path, file_crc)
    except ValueError as e:
      sort_file(tmp_file_path, 'failed', file_crc)

    os.remove(tmp_file_path)
    os.remove(file_path)

  # file_name = path.basename(file_path)
  # file_dir = path.dirname(file_path)

  # file_ext = file_name.split('.')[-1]

  # if file_ext == 'zip':
  #   with ZipFile(file_path, 'r') as zipfile:
  #     inner_files = zipfile.filelist

  #     zipfile.extractall('tmp')

  #     for inner_file in inner_files:
  #       extracted_file = f'tmp/{inner_file.filename}'
  #       file_crc = crc(f'tmp/{inner_file.filename}')
  #       file_info = get_file_info(inner_file.filename, file_crc)
  # else:
  #   sh.copy(file_path, 'tmp')
  #   file_crc = crc(f'tmp/{file_name}')
  #   file_info = get_file_info(file_name, file_crc)


def ingest(path: str) -> None:
  file_paths = find_files(path)

  for file_path in file_paths:
    ingest_file(file_path)