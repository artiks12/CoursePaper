import json
from DataFetchers.DataAuthor import DataAuthor

class DataContent():
    def __init__(self, contentType = '', publicationDate = '', authors = [], content = ''):
        self.ContentType: str = contentType
        self.PublicationDate: str = publicationDate
        self.Authors: list[DataAuthor] = authors
        self.Content: str = content

    def to_json(self):
        return {
            'Tips': self.ContentType,
            'Datums': self.PublicationDate,
            'Autori': [author.to_json() for author in self.Authors] ,
            'Saturs': self.Content
        }
    
    @classmethod
    def from_json(self, data):
        return self(data['Tips'], data['Datums'], [DataAuthor().from_json(author) for author in data['Autori']], data['Saturs'])