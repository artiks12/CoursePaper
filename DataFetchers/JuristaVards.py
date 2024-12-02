
from pyquery import PyQuery as pq
from datetime import datetime
import time
from DataFetchers.DataFetcher import DataFetcher
from DataFetchers.DataSource import DataSource
from DataFetchers.DataContent import DataContent
from DataFetchers.DataAuthor import DataAuthor

topics = {
    9001:"Administratīvā atbildība",
    4576:"Administratīvās tiesības un process",
    8493:"Apdrošināšanas tiesības",
    8649:"Bērna tiesības",
    8560:"Būvniecības tiesības",
    4591:"Cilvēktiesības",
    4577:"Civiltiesības un process",
    4578:"Darba tiesības",
    7704:"Datu apstrāde",
    11988:"Dzīvnieku aizsardzība",
    11034:"E-lieta",
    4589:"Eiropas tiesības",
    9572:"Enerģētikas tiesības",
    9403:"ES fondi",
    13562:"Fintech",
    4582:"Intelektuālā īpašuma tiesības",
    10605:"Interešu pārstāvība",
    7269:"Īres tiesības",
    10091:"Juridiskā tehnika un valoda",
    4579:"Komerctiesības",
    4580:"Konkurences tiesības",
    4586:"Konstitucionālās tiesības",
    4662:"Maksātnespējas process",
    4583:"Medicīnas tiesības",
    4581:"Patērētāju tiesības",
    4584:"Šķīrējtiesu process",
    4585:"Krimināltiesības un process",
    11518:"Militārās tiesības",
    8577:"Nolēmumu piespiedu izpilde",
    13063:"Noziedzīgi iegūtu līdzekļu legalizācijas novēršana",
    11152:"Pacientu tiesības",
    8482:"Pašvaldību tiesības",
    11819:"Policijas tiesības",
    10067:"Profesionālā ētika",
    7518:"Publiskie iepirkumi",
    11224:"Sankcijas",
    4669:"Sociālās tiesības",
    13612:"Sports un tiesības",
    9548:"Starptautiskās privāttiesības",
    4587:"Starptautiskās tiesības",
    8039:"Tehnoloģijas un mākslīgais intelekts",
    8857:"Mākslīgais intelekts",
    10120:"Tiesību politika un prakse Covid-19 apstākļos",
    4588:"Tiesību teorija, vēsture un filozofija",
    11946:"Tiesu darba organizācija",
    4590:"Tiesu iekārta",
    11565:"Trauksmes celšana",
    7725:"Tūrisma tiesības",
    9588:"Valsts pārvalde",
    11739:"Valsts un baznīca",
    8561:"Vides tiesības",
}

PATH = f'../Data/juristavards'

baseUrl = 'https://juristavards.lv'
listUrlPath = '/arhivs.php?k=viss&pageset=50'
listItemsElem = 'div.arhivs-list div.item'
listItemUrlElem = 'div.wrapper a.title'
pageParam = '&page='
periodParam = '&d=df,dt'
dateFormat = '%d/%m/%y'
timeout = True
topicParam = '&n='

class JuristaVards(DataFetcher):
    def __init__(self): 
        super().__init__(baseUrl, listUrlPath, listItemsElem, listItemUrlElem, pageParam, periodParam, dateFormat, timeout, topicParam)

    def __get_datetime(self, date_string: str):
        if date_string.strip() == '' or date_string == None: return None
        parts = date_string.split(' ')[0:3]

        day = int(parts[0][:-1])
        year = int(parts[2])
        month = -1
        
        if parts[1].strip().upper() == 'JANVĀRIS': month = 1
        if parts[1].strip().upper() == 'FEBRUĀRIS': month = 2
        if parts[1].strip().upper() == 'MARTS': month = 3
        if parts[1].strip().upper() == 'APRĪLIS': month = 4
        if parts[1].strip().upper() == 'MAIJS': month = 5
        if parts[1].strip().upper() == 'JŪNIJS': month = 6
        if parts[1].strip().upper() == 'JŪLIJS': month = 7
        if parts[1].strip().upper() == 'AUGUSTS': month = 8
        if parts[1].strip().upper() == 'SEPTEMBRIS': month = 9
        if parts[1].strip().upper() == 'OKTOBRIS': month = 10
        if parts[1].strip().upper() == 'NOVEMBRIS': month = 11
        if parts[1].strip().upper() == 'DECEMBRIS': month = 12

        return datetime(year=year, month=month, day=day).strftime('%Y-%m-%d')
    
    def _getAuthors(self, authorsTag):
        if len(authorsTag) == 0: return []

        authors = authorsTag('div.author-list div.item')
        result = []
        if len(authors) > 0:
            for author in authors.items():
                degree = author('div.right div.grads').text()
                name = author('div.right a').text()
                name = degree + ' ' + name if degree != '' else name
                details = author('div.right div.tituls').text().strip()
                result.append(DataAuthor(name, details))
        else:
            departments = authorsTag('div.author-list div.author-list.only-list a')
            for department in departments.items():
                result.append(DataAuthor(department.text(), ''))

        return result
    
    def fetchData(self, urls, topic = None):
        all_entries = []
        for url in urls:
            entry = DataSource()
            abstract = DataContent()
            article = DataContent()
            html_content, final_url = self._get_html_content(url)
            if html_content:
                entry.Url = final_url
                all_content = pq(html_content)
                content_tag = all_content('div.doc-left')
                
                entry.Topic = content_tag('div.margin-1 a').text() if topic == None else topic

                title = content_tag('div.title')

                for title in content_tag('div.title').items():
                    entry.Title =title.text()
                    break

                if content_tag('div#paid_content_info').html() != None: entry.Subscription = True

                article.PublicationDate = self.__get_datetime(content_tag('div.margin-1 div.datums').text()) 
                article.ContentType = 'Raksts'
                article.Authors = self._getAuthors(content_tag('div.author_and_publisher'))
                article.Content = content_tag('div.teksts').html(method='html')
                
                if article.Content != None: article.Content = article.Content.strip()

                abstract.ContentType = 'Anotācija'
                abstract.Content = content_tag('div.anotacija').html(method='html')

                if abstract.Content != None: abstract.Content = abstract.Content.strip()
            
                entry.Contents = [abstract, article]

                all_entries.append(entry)
            else:
                print('Fail:',url)
            time.sleep(1)
        
        return all_entries