import asyncio

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage

connection = None
chanel = None
logs_exchange = []
queue = None


async def start():
    global connection
    global chanel
    global logs_exchange
    global queue
    connection = await connect("amqp://user:password@localhost/")
    channel = await connection.channel()
    #        await channel.set_qos(prefetch_count=1)

    logs_exchange = []
    for i in range(5):
        logs_exchange.append(None)
        logs_exchange[i] = await channel.declare_exchange(
            "ex" + str(i), ExchangeType.FANOUT,
            )
    queue = await channel.declare_queue(exclusive=True)


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        print(f"[x] {message.body!r}")


async def background():
    global queue
    for i in range(5):
        await asyncio.sleep(5)
        await queue.bind(logs_exchange[i])


async def recv() -> None:
    # Perform connection

        # Creating a channel

        # Declaring queue

        # Binding the queue to the exchange
    # await queue.bind(logs_exchange)

        # Start listening the queue
    await queue.consume(on_message)

    print(" [*] Waiting for logs. To exit press CTRL+C")
    await asyncio.Future()


async def main():
    await start()
    t1 = asyncio.create_task(recv())
    t2 = asyncio.create_task(background())
    await t1
    await t2

asyncio.run(main())



# import pika
#
# credentials = pika.PlainCredentials('user', 'password')
# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
# channel = connection.channel()
#
# channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
#
# result = channel.queue_declare(queue='', exclusive=True)
# queue_name = result.method.queue
#
# channel.queue_bind(
#     exchange='direct_logs', queue=queue_name, routing_key='key')
#
# def callback(ch, method, properties, body):
#     print(" [x] %r:%r" % (method.routing_key, body))
#
#
# channel.basic_consume(
#     queue=queue_name, on_message_callback=callback, auto_ack=True)
#
# input()
# channel.start_consuming()
# print("Something")