from dotenv import dotenv_values

from ingest import Ingester


if __name__ == '__main__':
  config = dotenv_values(".env")

  ingester = Ingester(
    backlog_dir = '../backlog',
    depot_dir = '../depot',
    failed_dir = '../failed'
  )

  ingester.ingest()