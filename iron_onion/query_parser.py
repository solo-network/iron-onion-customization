import logging
import os
import json
from dataclasses import dataclass, field
from typing import Optional, Dict
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryParser:
    iron_event_id: Optional[str] = None
    data_loaded: [Dict] = field(default_factory=dict)
    query_data = os.path.join(os.path.dirname(__file__), 'query.json')

    def get_query_data(self):
        with open(self.query_data, 'r') as file:
            load_data = json.load(file)
            self.data_loaded = load_data

    def get_buckets(self, qyery_data):
        try:
            buckets = data['aggregations']['event_count']['buckets']
            return buckets

        except Exception as error:
            print(error)

    def handling_buckets(self, buckets):
        for bucket in buckets:
            log_event_id = bucket['key']
            hits = bucket['show_fields']['hits']['hits']
            log_doc_count = bucket['doc_count']
            print(log_doc_count)

    def set_iron_id(self):
        self.data_loaded['iron_event_id'] = uuid.uuid4()
    



if __name__ == "__main__":
    obj = QueryParser()
    obj.get_query_data()
    obj.set_iron_id()
    print(obj.data_loaded)
