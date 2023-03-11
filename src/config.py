from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv('URL')
DATA = os.getenv('DATA')
WORKER_NAME = os.getenv('WORKER_NAME')
SEARCH_MODE = os.getenv('SEARCH_MODE')
