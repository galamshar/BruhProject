import re
import sys
import pika
from pika.adapters.blocking_connection import BlockingChannel

def get_arg_value(flag: str) -> str:
    return sys.argv[sys.argv.index(flag) + 1]

def connect_to_rabbit():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=get_arg_value('-host'),
        virtual_host=get_arg_value('-vhost'),
        credentials=pika.PlainCredentials(get_arg_value('-username'), get_arg_value('-password'))))

    channel = connection.channel()

    return connection, channel

def send_file(filepath: str, channel: BlockingChannel):
    body = ''

    with open(filepath) as file:
        body = file.read()

    channel.basic_publish(get_arg_value('-exchange'), routing_key='', body=body)

def main():
    connection, channel = connect_to_rabbit()

    while True:
        filepath = input()

        if filepath == 'exit':
            break

        send_file(filepath, channel)

    channel.close()
    connection.close()


if __name__ == '__main__':
    main()
