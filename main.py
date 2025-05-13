from src.codejson import CodeJson
from src.config import Config
from src.repository import Repository

from datetime import datetime
import sys

def main():
  now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
  print(now)
  errors, isVerified = Config().verify()
  if errors or not isVerified:
    print(f'Exiting due to bad credentials in configuration: {errors}')
    sys.exit()

  codejson = CodeJson()
  print(codejson.get_required_project_fields())

if __name__ == "__main__":
  main()
