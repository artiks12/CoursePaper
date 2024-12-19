from DataFetchers.JuristaVards import JuristaVards, PATH as juristaVardsPath, topics as juristaVardsTopics
from DataFetchers.LvPortals import LvPortals, PATH as lvPortalsPath
from DataFetchers.DataFetcher import DataFetcher

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

def Execute(site, Fetcher: DataFetcher, savePath, filename = f'dati_{datetime.now().strftime('%Y-%m-%d')}.json', topics = {}):
    configPath = 'DataFetchers/config.json'

    config = None
    with open(configPath,'r',encoding='utf-8') as f:
        config = json.load(f)

    end = datetime.today() - timedelta(days=1)

    if config[site]['nextExecute'] != '':
        start: datetime = datetime.strptime(config[site]['nextExecute'],'%Y-%m-%d')
    else:
        # start: datetime = datetime(year=1990,month=1,day=1)
        start: datetime = datetime(year=1996,month=1,day=1) # JuristaVards

    checkpoint = start + relativedelta(months=1)
    if len(topics) > 0:
        checkpoint = datetime(year=end.year, month=end.month, day=1) - timedelta(days=1)
        for topic in topics.keys():
            filename = f'dati_{start.year}_{0 if start.month < 10 else ''}{start.month}_{topics[topic]}.json'
            
            articles = Fetcher.fetchArticles(start, checkpoint, topic)
            data = Fetcher.fetchData(articles, topics[topic])
            
            Fetcher.WriteData(data, filename, savePath)
            # Fetcher.AppendHistoryData(data, filename, savePath)

        config[site]['nextExecute'] = (checkpoint + timedelta(days=1)).strftime('%Y-%m-%d')

        with open(configPath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    else:
        while checkpoint <= end:
            filename = f'dati_{start.year}_{0 if start.month < 10 else ''}{start.month}.json'
            if checkpoint > end: checkpoint = end
            
            articles = Fetcher.fetchArticles(start, checkpoint, None)
            data = Fetcher.fetchData(articles)
            
            Fetcher.WriteData(data, filename, savePath)
            # Fetcher.AppendHistoryData(data, filename, savePath)

            config[site]['nextExecute'] = checkpoint.strftime('%Y-%m-%d')

            with open(configPath, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)

            start: datetime = checkpoint
            checkpoint = start + relativedelta(months=1)


# Execute('lvportals', LvPortals(), lvPortalsPath, 'dati.json')
# Execute('juristavards', JuristaVards(), juristaVardsPath, 'dati.json', juristaVardsTopics)
