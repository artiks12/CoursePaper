from pyquery import PyQuery as pq
from datetime import datetime
from DataFetchers.DataFetcher import DataFetcher
from DataFetchers.DataSource import DataSource
from DataFetchers.DataContent import DataContent
from DataFetchers.DataAuthor import DataAuthor
import time

PATH = f'../Data/juristavards'

baseUrl = 'https://www.vestnesis.lv'
listUrlPath = '/rezultati/atbilstiba/on/locijums/on/skaits/100'
listItemsElem = 'div#resultCards div.block a'
listItemUrlElem = ''
pageParam = '/lapa/'
periodParam = '/kartot/datums/datumi/publicets-df-dt'
dateFormat = '%d.%m.%Y.'
timeout = True

class Vestnesis(DataFetcher):
    def __init__(self): 
        super().__init__(baseUrl, listUrlPath, listItemsElem, listItemUrlElem, pageParam, periodParam, dateFormat, timeout)
