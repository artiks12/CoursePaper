import json

class DataAuthor():
    def __init__(self, name = '', details = ''):
        self.Name: str = name
        self.Details: str = details

    @classmethod
    def from_json(self, data):
        return self(data['Vārds'], data['Detaļas'])
    
    def to_json(self):
        return {
            'Vārds': self.Name,
            'Detaļas': self.Details
        }