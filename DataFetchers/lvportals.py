from pyquery import PyQuery as pq
from datetime import datetime
from DataFetchers.DataFetcher import DataFetcher
from DataFetchers.DataSource import DataSource
from DataFetchers.DataContent import DataContent
from DataFetchers.DataAuthor import DataAuthor

PATH = f'../Data/lvportals'

baseUrl = 'https://lvportals.lv/e-konsultacijas'
listUrlPath = '/visas-atbildes'
listItemsElem = 'div.cardsWrapper div.card'
listItemUrlElem = 'div.title a'
pageParam = '/lapa:'
periodParam = '/no:df/lidz:dt'
dateFormat = '%d.%m.%Y.'
timeout = False
topicParam = '/tema:'

class LvPortals(DataFetcher):
    def __init__(self): 
        super().__init__(baseUrl, listUrlPath, listItemsElem, listItemUrlElem, pageParam, periodParam, dateFormat, timeout)
        
    def __get_datetime(self, date_string: str):
        if date_string == 'Šodien': return datetime.today().strftime('%Y-%m-%d')
        if date_string.strip() == '' or date_string == None: return None
        parts1 = date_string.split('.')
        parts2 = parts1[1].split(',')

        day = int(parts1[0])
        year = int(parts2[1])
        month = -1
        
        if parts2[0].strip() == 'janvārī': month = 1
        if parts2[0].strip() == 'februārī': month = 2
        if parts2[0].strip() == 'martā': month = 3
        if parts2[0].strip() == 'aprīlī': month = 4
        if parts2[0].strip() == 'maijā': month = 5
        if parts2[0].strip() == 'jūnijā': month = 6
        if parts2[0].strip() == 'jūlijā': month = 7
        if parts2[0].strip() == 'augustā': month = 8
        if parts2[0].strip() == 'septembrī': month = 9
        if parts2[0].strip() == 'oktobrī': month = 10
        if parts2[0].strip() == 'novembrī': month = 11
        if parts2[0].strip() == 'decembrī': month = 12

        return datetime(year=year, month=month, day=day).strftime('%Y-%m-%d')
    
    def fetchData(self, urls, topic = None):
        all_entries = []
        for url in urls:
            entry = DataSource()
            question = DataContent()
            answer = DataContent()
            html_content, final_url = self._get_html_content(url)
            if html_content:
                entry.Url = final_url
                all_content = pq(html_content)
                
                topic_tag = all_content('div.data.section.eKonsultacijas')
                entry.Topic = topic_tag.text()[6:]

                main_tag = all_content('div.articleContent')
                entry.Title = main_tag('h1').text()

                content_tag = main_tag('div.eKonsultacijas')
                
                question_tag = content_tag('div.blockContainer.noBottom.articleQuestion')
                question.ContentType = 'Jautājums'
                question.PublicationDate =  self.__get_datetime(question_tag('div.blockData div.smallText').text())
                question.Authors = [DataAuthor(question_tag('div.blockData div.author').text())]
                question.Content = question_tag('div.article').html(method='html').strip()

                answer_tag = content_tag('div.blockContainer.noBottom.articleAnswer')
                answer.ContentType = 'Atbilde'
                answer.PublicationDate = self.__get_datetime(answer_tag('div.smallText').text())
                answer.Authors = [DataAuthor(author('a').text(), author('div.info').text()) for author in answer_tag('div.authors div div.text').items()] 
                answer.Content = answer_tag('div.article.stickyHeight').html(method='html').strip()
            
                entry.Contents = [question,answer]

                all_entries.append(entry)
        
        return all_entries