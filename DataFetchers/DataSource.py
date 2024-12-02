import json
from DataFetchers.DataContent import DataContent

class DataSource():
    def __init__(self, url = '', topics = '', title = '', contents = [], subscription = False):
        self.Url: str = url
        self.Topic: str = topics
        self.Title: str = title
        self.Contents: list[DataContent] = contents
        self.Subscription: bool = subscription

    def to_json(self):
        return {
            'URL': self.Url,
            'Tēma': self.Topic,
            'Nosaukums': self.Title,
            'Saturi': [content.to_json() for content in self.Contents],
            'Abonaments': self.Subscription
        }
    
    @classmethod
    def from_json(self, data):
        if 'Abonaments' not in data: subscription = False
        else: subscription = data['Abonaments']
        return self(data['URL'], data['Tēma'], data['Nosaukums'], [DataContent.from_json(content) for content in data['Saturi']], subscription)