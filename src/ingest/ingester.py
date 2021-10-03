import os
import shutil as sh

from os import path
from zipfile import ZipFile

from hashing import file_crc32

from . import init_dir, find_files
from .utils import create_dir, get_dest, send_failed_file, send_success_file

import json, requests

def get_file_info(
  file_name: str, 
  file_crc: str
) -> dict:
  request_url = f'https://www.screenscraper.fr/api2/jeuInfos.php?romtype=rom&output=json&crc={file_crc}&romnom={file_name}'

  response = requests.get(request_url)

  if response.status_code == 200:
    return json.loads(response.text)['response']
  else:
    raise ValueError(f'{response.status_code}:{file_name}:{file_crc}:{response.text}')


class Ingester():
  def __init__(
    self,
    backlog_dir: str,
    depot_dir: str,
    failed_dir: str
  ) -> None:
    init_dir(backlog_dir)
    init_dir(depot_dir)
    init_dir(failed_dir)

    self.backlog_dir = backlog_dir
    self.depot_dir = depot_dir
    self.failed_dir = failed_dir
    self.temp_dir = 'tmp'


  def ingest(self) -> None:
    file_paths = find_files(self.backlog_dir)

    for file_path in file_paths:
      self.ingest_file(file_path)


  def ingest_file(
    self, 
    file_path: str
  ) -> None:
    self.move_to_temp(file_path)
    temp_file_paths = find_files(self.temp_dir)

    for temp_file_path in temp_file_paths:
      file_crc = file_crc32(temp_file_path)
      file_name = path.basename(temp_file_path)

      try:
        file_info = get_file_info(file_name, file_crc)
        dest_path = get_dest(file_info)
        sort_path = create_dir(dest_path)
        send_success_file(temp_file_path, sort_path, file_crc, file_info)
      except ValueError as e:
        send_failed_file(temp_file_path, self.failed_dir, file_crc, str(e))

    os.remove(temp_file_path)
    os.remove(file_path)

  
  def move_to_temp(
    self, 
    file_path: str
  ) -> None:
    file_ext = file_path.split('.')[-1]

    if file_ext == 'zip':
      with ZipFile(file_path, 'r') as zipfile:
        inner_files = zipfile.filelist

        zipfile.extractall(self.temp_dir)

        file_list = []

        for inner_file in inner_files:
          file_list.append(inner_file.filename)

        return(file_list)
    else:
      file_name = path.basename(file_path)

      sh.copy(file_path, self.temp_dir)

      return [ file_name ]


  def close(self) -> None:
    os.remove(self.temp_dir)