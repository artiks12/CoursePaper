import requests
from pyquery import PyQuery as pq
from datetime import datetime, timedelta
import json
import time
import os
from DataFetchers.DataSource import DataSource

class DataFetcher:
    def __init__(self, baseUrl, listUrlPath, listItemsElem, listItemUrlElem, pageParam, periodParam, dateFormat, timeout, topicParam):
        self.__baseUrl: str = baseUrl
        self.__listUrlPath: str = listUrlPath
        self.__listItemsElem: str= listItemsElem
        self.__listItemUrlElem: str = listItemUrlElem
        self.__pageParam: str = pageParam
        self.__periodParam: str = periodParam
        self.__dateFormat: str = dateFormat
        self.__timeout: bool = timeout
        self.__topicParam: str = topicParam

    # This method was made by ChatGPT
    def _get_html_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            response.encoding = 'utf-8'
            
            final_url = response.url
            
            return response.text, final_url
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None, url
            
    def GetCleanTextFromHtml(self, content):
        return pq(content).text()
    
    def ReadData(self, data: list, filename: str, path: str) -> list[DataSource]:
        fullPath = f'{path}/{filename}'
        data = []
        with open(fullPath, encoding='utf-8') as f:
            data = [DataSource.from_json(entry) for entry in json.load(f)]

        return data
    
    def WriteData(self, data: list[DataSource], filename: str, path: str):
        if len(data) > 0:
            fullPath = f'{path}/{filename}'
            toWrite = [entry.to_json() for entry in data]
            
            with open(fullPath, 'w', encoding='utf-8') as f:
                json.dump(toWrite, f, ensure_ascii=False, indent=4)
        
    def RewriteHistoryData(self, data: list[DataSource], filename: str, path: str):
        if len(data) > 0:
            fullPath = f'{path}/{filename}'
            
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if os.path.isfile(fullPath):
                history: list[DataSource] = self.ReadData(data, filename, path)
                
                urls = [ entry.Url for entry in data]
                for entry in history:
                    if entry.Url not in urls: data.append(entry)
            
            self.WriteData(data, filename, path)

    def AppendHistoryData(self, data: list[DataSource], filename: str, path: str):
        if len(data) > 0:
            fullPath = f'{path}/{filename}'
            
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if os.path.isfile(fullPath):
                history: list[DataSource] = self.ReadData(data, filename, path)

                data.extend(history)
            
            self.WriteData(data, filename, path)

    def __constructPeriodParams(self, dateFrom: datetime, dateTo: datetime):
        result: str = self.__periodParam
        
        start = dateFrom
        end = dateTo - timedelta(days=1)
        
        result = result.replace('df',start.strftime(self.__dateFormat)).replace('dt',end.strftime(self.__dateFormat))

        return result
    
    def __constructPageParam(self, page):
        return self.__pageParam + str(page)
    
    def __constructTopicParam(self, topic):
        return self.__topicParam + str(topic) if topic != None and self.__topicParam != None else ''

    def fetchArticles(self, dateFrom: datetime, dateTo: datetime, topic):
        result = []
        page = 1
        while True:
            pageUrl = f'{self.__baseUrl}{self.__listUrlPath}{self.__constructPeriodParams(dateFrom, dateTo)}{self.__constructTopicParam(topic)}{self.__constructPageParam(page)}'
            print(pageUrl)
            html_content, _ = self._get_html_content(pageUrl)

            all_content = pq(html_content)

            article_list = all_content(self.__listItemsElem)

            if (len(article_list) == 0): 
                if self.__timeout: time.sleep(0.5)
                break
            
            for article in article_list.items():
                if self.__listItemUrlElem != '': articleUrl = article(self.__listItemUrlElem).attr('href')
                else: articleUrl = article.attr('href')
                if self.__baseUrl in str(articleUrl): result.append(str(articleUrl))
                else: result.append(self.__baseUrl + str(articleUrl))
            page += 1
            if self.__timeout: time.sleep(0.5)

        return result
    
    def fetchData(self, urls, topic):
        pass

    def getLawArticle(self, url: str, Nr: int):
        html_content, final_url = self._get_html_content(url)
        if html_content:
            all_content = pq(html_content)
            title = all_content('div.TV207').text()

            articles = all_content('div.TV213').items()

            article = None
            for temp in articles:
                if temp.attr('data-num') == Nr: article = temp

            print(article.text())
