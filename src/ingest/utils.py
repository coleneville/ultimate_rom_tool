import os


def find_files(path: str) -> list:
  files = []
  
  for root, _, file_names in os.walk(path):
    for file_name in file_names:
      files.append(f'{root}/{file_name}')

  return files