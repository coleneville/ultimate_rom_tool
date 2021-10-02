import zlib

def file_crc32(filepath) -> str:
  BUF_SIZE = 65536

  with open(filepath, 'rb') as infile:
    hash = 0
    data = infile.read(BUF_SIZE)

    while data:
      hash = zlib.crc32(data, hash)
      data = infile.read(BUF_SIZE)

    return "%08X" % (hash & 0xFFFFFFFF)