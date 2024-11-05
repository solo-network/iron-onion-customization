import requests
import json
import os
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class IronXIncident:
    url: str = "http://localhost:8000/api/incident/"
    customer_id: str = ''
    token: str = ''
    incident_name: str = ''
    incident_description: str = ''
    priority: str = ''
    siem_link: str = ''
    asset_target: str = ''
    observer_product: str = ''
    source_event_id: str = ''
    artifact: str = ''

    def create_incident(self):
        headers={"Authorization": "Token "+self.token,
                 "Content-Type": "application/json"}
        payload2 = {
                    "customer_id": "127d3a07-fedc-4ff0-8f75-6d983dfe9f54",
                    "incident_name": self.incident_name,
                    "incident_description": self.incident_description,
                    "priority": self.priority,
                    "siem_link": self.siem_link,
                    "asset_target": self.asset_target,
                    "observer_product": self.observer_product,
                    "source_event_id": self.source_event_id,
                    "artifact": self.artifact
                }
        try:
          response = requests.post(self.url, headers=headers, json=payload2)
          print(response.text)
        except Exception as error:
          print(error)