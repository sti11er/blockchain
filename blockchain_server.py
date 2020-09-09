import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests


from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.nodes = set()


    # возвращает последний блок в цепочке
    @property
    def last_block(self):
        return self.chain[-1];

    @staticmethod
    def hash(block):
        """
        Создает хэш SHA-256 блока
        : param block: <dict> Блок
        : return: <str>
        """

        # Мы должны убедиться, что словарь упорядочен, иначе у нас будут несогласованные хэши.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Проверяет доказательство: содержит ли хэш (last_proof, proof) 4 ведущих нуля?
        : param last_proof: <int> Предыдущее доказательство
        : param proof: <int> Текущее доказательство
        : return: <bool> Истинно, если верно, если нет.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
        

    def register_node(self, address):
        """
        Добавить новый узел в список узлов
        : param address: <str> Адрес узла. 
        : return: Нет
        """

        parsed_url = urlparse(address)
        print(parsed_url)
        self.nodes.add(parsed_url.netloc)


    def valid_chain(self, chain):
        """
        Определите, действителен ли данный блокчейн
        : param chain: <список> Блокчейн
        : return: <bool> Истина, если действительна, ложь, если нет
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")

            # Проверяем, что хеш блока правильный
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Проверьте правильность Proof of Work
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1


        return True



    def resolve_conflicts(self, node_user):
        """
        Это наш алгоритм консенсуса, он разрешает конфликты
        заменив нашу цепочку на самую длинную в сети.
        : return: <bool> Истина, если наша цепочка была заменена, Ложь, если нет
        """

        our_chain = requests.get(f'{node_user}chain')
        neighbours = self.nodes
        new_chain = None


        # Мы ищем только цепочки длиннее нашей
        max_length = our_chain.json()['length']

        # Проверем цепочки со всех узлов в нашей сети
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Проверим что длина больше максимальной и цепочка действительна
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

 
        if new_chain:
            return new_chain

        return False


# Создаем экземпляр нашего узла
app = Flask(__name__)

# Создаем глобально уникальный адрес для этого узла
node_identifier = str(uuid4()).replace('-', '')

# Создаем экземпляр блокчейна
blockchain = Blockchain()


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['POST'])
def consensus():
    values = request.get_json()

    node = values.get('node')
    replaced = blockchain.resolve_conflicts(node)
    if replaced:
        response = {
            'message': 'Your chain was replaced',
            'Authoritative chain': replace
        }
    else:
        response = {
            'message': 'Your chain is authoritative'
        }

    return jsonify(response), 200

    return jsonify(replaced), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)