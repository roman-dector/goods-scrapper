import os
from dotenv import load_dotenv


load_dotenv()

ROOT_DIR = os.environ['ROOT_DIR']

DB_PATH = os.environ['ROOT_DIR'] + 'src/assets/goods_scrapper.db'

EXCEL_INPUT_PATH = os.environ['ROOT_DIR'] + 'src/assets/test_product_links.xlsx'

EXCEL_RESULT_PATH = os.environ['ROOT_DIR'] + 'src/assets/result_sheet.xlsx'
