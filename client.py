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
        self.chain = []
        self.current_transactions = []

        # блок без предшественников
        self.new_block(previous_hash=1, proof=100)


    # возвращает последний блок в цепочке
    @property
    def last_block(self):
        return self.chain[-1]

    def new_block(self, proof, previous_hash=None):
        """
        Cоздаем новый блок
        : param proof: <int> Доказательство алгоритма Proof of Work
        : param previous_hash: (Необязательно) <str> Хеш предыдущего блока
        : return: <dict> Новый блок
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Сбросим текущий список транзакций
        self.current_transactions = []
        self.chain.append(block)

        return block

    
    # создаем новую транзакцию
    def new_transaction(self, sender, recipient, amount):
        """
        Создает новую транзакцию для перехода в следующий добытый блок
        : param sender: <str> Адрес отправителя
        : param recipient: <str> Адрес Получателя
        : param amount: <int> Количество
        : return: <int> Индекс блока, который будет содержать эту транзакцию
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

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

    def proof_of_work(self, last_proof):
        """
        Простой алгоритм доказательства работы:
         - Найдите число p 'такое, что hash (pp') содержит четыре ведущих нуля, где p - предыдущий p '
         - p - предыдущее доказательство, а p '- новое доказательство.
        : param last_proof: <int>
        : return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

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

    def my_money(self, node_identifier):
        """
        Считает количество денег пользователя
        : param proof: <int> Идентификатор узла пользователя
        : return: <int> Количество денег пользователя
        """

        chain = self.chain
        money = 0

        for block in chain:
            if len(block['transactions']) > 0:
                if block['transactions'][0]['sender'] == node_identifier:
                    money -= block['transactions'][0]['amount']
                elif block['transactions'][0]['recipient'] == node_identifier:
                    money += block['transactions'][0]['amount']
        
        return money


# Создаем экземпляр нашего узла
app = Flask(__name__)

# Создаем глобально уникальный адрес для этого узла
node_identifier = str(uuid4()).replace('-', '')

# Создаем экземпляр блокчейна
blockchain = Blockchain()


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Убедитесь, что обязательные поля есть в данных POST
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Создать новую транзакцию
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    # Мы запускаем алгоритм доказательства работы, чтобы получить следующее доказательство ...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Мы должны получить вознаграждение за доказательство.
    # Отправитель «0» означает, что этот узел добыл новую монету.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Создайте новый блок, добавив его в цепочку
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/my_money', methods=['GET'])
def my_money():
    money = blockchain.my_money(node_identifier)

    return jsonify(f'You have {money} coins'), 200


@app.route('/chain_update', methods=['POST'])
def chain_update():
    values = request.get_json()

    headers = {'Content-type': 'application/json',  # Определение типа данных
            'Accept': 'text/plain',
            'Content-Encoding': 'utf-8'}

    server = values.get('server')
    client = values.get('client')

    data = {'node': client}
    result = requests.post(f"{server}nodes/resolve", data=json.dumps(data), headers=headers)
    result = result.json()

    if result:
        blockchain.chain = result
        inf = "Your chain has been updated to a newer one"
    else:
        inf = "Your chain is authoritative"

    return jsonify(inf), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)