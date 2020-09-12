# blockchain

blockchain API на python.

Мой блокчейн разделен на сервер и клиент. 
Сервер может регистрировать пользователей и проверять их цепочки, 
a клиент - майнить, создавать транзакции просматривать свою цепочку.


Так выглядит блок
```python
block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

Запуск сервера:
```
python server.py
```
Запуск клиента:
```
python client.py -p 5001
```


```
http://localhost:5000 является url сервером
http://localhost:5000 являутся url клиента
```
server 
------
регистрация нового узла
```
curl -X POST -H "Content-Type: application/json" -d '{
 "nodes": ["http://localhost:5001/"]
}' "http://localhost:5000/nodes/register"
```

проверка нашей цепочки на авторитетность и правильность 
```
curl -X POST -H "Content-Type: application/json" -d '{
 "node": "http://localhost:5001/"
}' "http://localhost:5000/nodes/resolve"
```


client
------ 

создание транзакции 
```
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "3e0946620c2b4c959dd1c480d742357c",
 "recipient": "35909324a6a54bba9451cb0d4632f393",
 "amount": 5
}' "http://localhost:5001/transactions/new"
```
майнинг

```
curl http://localhost:5001/mine
```

просморт нашей цепочки
```
curl http://localhost:5001/chain
```

обновление нашей цепочки на более длинную если такая есть
```
curl -X POST -H "Content-Type: application/json" -d '{
 "server": "http://localhost:5000/",
 "client": "http://localhost:5001/"
}' "http://localhost:5001/chain_update"
```

просмотр наших денег
```
curl http://localhost:5001/my_money
```
