import logging
from dataclasses import dataclass, field
import json
import requests
import os
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IronCustomOnion:
    action: str
    file_name: str = None  # Nome do arquivo para a opção 'one_rule'
    elastic_url: str = field(default_factory=lambda: os.getenv('ELASTIC_URL', 'https://localhost:9200/.ds-logs-*/_search'))
    username: str = field(default_factory=lambda: os.getenv('ELASTIC_USER', 'teste'))
    password: str = field(default_factory=lambda: os.getenv('ELASTIC_PASSWORD', 'teste'))

    def __post_init__(self):
        self._execute_action()

    def _execute_action(self):
        if self.action == "folder_rules":
            self.folder_rules()
        elif self.action == "one_rule":
            if self.file_name:
                self.one_rule(self.file_name)
            else:
                logger.error("Para a ação 'one_rule', forneça o nome do arquivo como segundo argumento.")
        else:
            print("Ação inválida. Escolha 'folder_rules' ou 'one_rule'.")

    def folder_rules(self):
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules')

        if not os.path.exists(rules_path):
            print(f"Pasta 'rules' não encontrada em {rules_path}.")
            return

        for filename in os.listdir(rules_path):
            file_path = os.path.join(rules_path, filename)

            if os.path.isfile(file_path) and filename.endswith('.json'):
                print(f"Processando o arquivo: {filename}")
                self._process_rule(file_path)

    def one_rule(self, file_name):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules', file_name)
        print(file_path)

        if os.path.isfile(file_path):
            print(f"Processando o arquivo único: {file_name}")
            self._process_rule(file_path)
        else:
            logger.error(f"O arquivo '{file_name}' não foi encontrado na pasta 'rules'.")

    def _process_rule(self, file_path):
        """Carrega e envia o arquivo JSON para o Elasticsearch."""
        try:
            with open(file_path, 'r') as query_file_handle:
                query_json = json.load(query_file_handle)
                print(query_json)
            
            if not query_json:
                logger.warning(f"O arquivo '{file_path}' está vazio ou sem regras válidas.")
                return
            
            response = self.send_to_elastic(query_json)
            print(f"Resposta do Elasticsearch para {os.path.basename(file_path)}:\n{response}\n")

        except json.JSONDecodeError as json_err:
            logger.error(f"Erro de sintaxe JSON no arquivo '{file_path}': {json_err}")
        except requests.RequestException as req_err:
            logger.error(f"Erro ao executar a query para '{file_path}': {req_err}")
        except Exception as e:
            logger.error(f"Erro inesperado no arquivo '{file_path}': {e}")

    def send_to_elastic(self, query_json):
        """Envia a requisição POST para o Elasticsearch."""
        response = requests.post(
            url=self.elastic_url,
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"},
            json=query_json,
            verify=False
        )
        return response.json

    def set_iron_id(self):
        iron_id = uuid.uuid4()
        print(iron_id)

if __name__ == "__main__":
    obj = IronCustomOnion('one_rule')
    obj.set_iron_id()