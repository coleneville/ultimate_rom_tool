import os
from os import path

import json
from zipfile import ZipFile


def find_files(path: str) -> list:
  files = []
  
  for root, _, file_names in os.walk(path):
    for file_name in file_names:
      files.append(f'{root}/{file_name}')

  return files


def init_dir(dir: str):
  if dir[-1] == '/':
    dir = dir[:-1]
  
  dir_name = path.basename(dir)
  dir_path = path.dirname(dir)

  if dir_name not in os.listdir(dir_path):
    os.mkdir(dir)


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


def create_dir(base_dir: str, path: list) -> str:
  path_str = base_dir

  for part in path:
    part = str(part).replace('.', '')
    if part not in os.listdir(path_str):
      os.mkdir(f'{path_str}/{part}')

    path_str += f'/{part}'
  
  return path_str


def send_failed_file(
  file_path: str, 
  dest: str,
  file_crc: str, 
  message: str
) -> None:
  with open(f'{dest}/.log', 'a') as file:
    file.write(message)

  send_file(file_path, dest, file_crc)


def send_success_file(
  file_path: str,
  dest: str, 
  file_crc: str, 
  file_info: str
) -> None:
  with open(f'{dest}/game_info.json', 'w') as file:
    file.write(json.dumps(file_info['jeu']))

  send_file(file_path, dest, file_crc)


def send_file(file_path: str, dest: str, file_crc: str) -> None:
  zip_file = f'{dest}/{file_crc}.zip'

  if not os.path.isfile(zip_file):
    with ZipFile(zip_file, 'w') as file:
      os.chdir('tmp')
      file.write(file_path.split('/')[-1])
      os.chdir('..')