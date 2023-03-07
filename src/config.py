import os
from python-dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

URL = os.environ.get('URL')
