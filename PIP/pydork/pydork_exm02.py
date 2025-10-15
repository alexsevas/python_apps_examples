# conda activate allpy311

import urllib3
import warnings
from pydork.engine import SearchEngine
from pprint import pprint

# Подавляем только InsecureRequestWarning от urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Или более общий способ через warnings:
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')

search_engine = SearchEngine()
search_engine.set('bing') #google, duckduckgo
search_result = search_engine.search('chat gpt')

pprint(search_result)