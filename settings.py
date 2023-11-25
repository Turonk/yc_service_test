import json
import os

from dotenv import load_dotenv

load_dotenv()
CLOUD_ID = os.environ['CLOUD_ID']
TOKEN = os.environ['TOKEN']

with open('D:\\yandex_cloud\\key.json', 'r') as infile:
    SERVICE_ACC_CREDENTIALS = json.load(infile)
