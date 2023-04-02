import pika
import time

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

for i in range(5):
    channel.exchange_declare(exchange='ex' + str(i), exchange_type='fanout')

i = 0
while True:
    time.sleep(1)
    for j in range(5):
        channel.basic_publish(
            exchange='ex' + str(j), routing_key='', body='Some msg ' + str(i) + " " + str(j))
    i += 1