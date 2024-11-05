from iron_onion.query_handler import IronCustomOnion
import argparse

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

    query = IronCustomOnion(action=args.action, file_name=getattr(args, 'file_name', None))
    print(query)

if __name__ == "__main__":
    main()