# conda activate allpy311

# search text at google, bing, duckduckgo, with selenium
#$ pydork search -s -n 10 -t google bing duckduckgo -- 'super mario'

from pydork.engine import SearchEngine
from pprint import pprint

# SearchEngine
search_engine = SearchEngine()

search_engine.set('bing')
search_result = search_engine.search('hot news')

pprint(search_result)