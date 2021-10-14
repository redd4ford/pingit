import json
from config import Config
from device import DefaultGateway, Switch


def log(network: str, node, custom_status=None) -> None:
    print(f'{network}_{node.index}/{node.name} : '
          f'{custom_status if custom_status else node.status.value}')


def has_children(node) -> bool:
    return type(node) in [DefaultGateway, Switch] and len(node.children) > 0


def dict_to_str(network_as_dict: dict) -> str:
    return f'{network_as_dict}'.replace("\'", "\"")


def load_json_to_obj(filename: str = 'addresses.json'):
    with open(filename, encoding='utf-8') as f:
        json_tree = json.loads(f.read())   # as a list of dicts
        network_counter = 0
        for network in json_tree:
            Config.USER['networks'][f'{network_counter}'] = \
                DefaultGateway(**json.loads(dict_to_str(network)))
            network_counter += 1
