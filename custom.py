import logging
from dataclasses import dataclass, field
import argparse
import json
import requests
import os

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
        rules_path = os.path.join(os.path.dirname(__file__), 'rules')

        if not os.path.exists(rules_path):
            print(f"Pasta 'rules' não encontrada em {rules_path}.")
            return

        for filename in os.listdir(rules_path):
            file_path = os.path.join(rules_path, filename)

            if os.path.isfile(file_path) and filename.endswith('.json'):
                print(f"Processando o arquivo: {filename}")
                self._process_rule(file_path)

    def one_rule(self, file_name):
        file_path = os.path.join(os.path.dirname(__file__), 'rules', file_name)

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
        return response.text

def main():
    parser = argparse.ArgumentParser(
        description="Este script executa regras para interagir com o Elasticsearch do Security Onion da Solo Iron.",
        epilog="Exemplo de uso: python custom.py folder_rules ou python custom.py one_rule regrax.json"
    )
    subparsers = parser.add_subparsers(dest='action', required=True)

    parser_folder_rules = subparsers.add_parser(
        "folder_rules",
        help="Executa todas as regras encontradas na pasta 'rules'."
    )

    parser_one_rule = subparsers.add_parser(
        "one_rule",
        help="Executa uma única regra especificada pelo nome do arquivo JSON."
    )
    parser_one_rule.add_argument(
        "file_name",
        help="Nome do arquivo JSON que contém a regra a ser executada (ex: regrax.json)."
    )

    args = parser.parse_args()
    IronCustomOnion(action=args.action, file_name=getattr(args, 'file_name', None))

if __name__ == "__main__":
    main()