
import logging
from dataclasses import dataclass
import argparse
import json
import requests

@dataclass
class IronCustomOnion:
    query_path: str
    elastic_url: str = "https://localhost:9200/.ds-logs-*/_search"
    username: str = "elastic-solo"
    password: str = "Uo2fUHC1YKQ05kFe13vv"
    query: str = ''


    def get_query(self):
        with open(self.query_path, 'r') as query_file_handle:
            self.query = json.load(query_file_handle)
            
        return self.query
 

    def execute(self, query_json):
        response = requests.post(url=self.elastic_url, auth=(self.username, self.password), headers={"Content-Type": "application/json"}, json=query_json, verify=False)
        return response.text

if __name__ == '__main__':
    engine = IronCustomOnion(query_path='/Users/felipeguimaraes/Documents/codes/iron-onion-customization/rules/regrax.json')
    query = engine.get_query()
    execution = engine.execute(query)
    print(execution)

