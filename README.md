# blockchain

blockchain API на python.

Мой блокчейн разделен на сервер и клиент. 
Сервер может регистрировать пользователей и проверять их цепочки, 
a клиент - майнить, создавать транзакции просматривать свою цепочку.

Запуск сервера:
```
python server.py
```
Запуск клиента:
```
python client.py -p 5001
```

server 
------
регистрация нового узла
```
curl -X POST -H "Content-Type: application/json" -d '{
 "nodes": ["url client"]
}' "url server/nodes/register"
```

проверка нашей цепочки на авторитетность и правильность 
```
curl -X POST -H "Content-Type: application/json" -d '{
 "node": "url client"
}' "url server/nodes/resolve"
```


client
------ 

создание транзакции 
```
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "-",
 "recipient": "-",
 "amount": -
}' "url client/transactions/new"
```
майнинг

```
curl -X GET url client/mine
```

просморт нашей цепочки
```
curl -X GET url client/chain
```
