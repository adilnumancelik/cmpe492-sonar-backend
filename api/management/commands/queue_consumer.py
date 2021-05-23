from django.core.management.base import BaseCommand, CommandError
import pika, os, time, sys, requests

SONAR_FETCHER_URL = "https://boun-sonar.herokuapp.com/fetch/"

class Command(BaseCommand):
    # create a function which is called on incoming messages
    def callback(self, ch, method, properties, body):
        body = body.decode('ascii')
        requests.get(SONAR_FETCHER_URL)

    def handle(self, *args, **options):
        # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
        url = os.environ.get('CLOUDAMQP_URL')
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel() # start a channel
        channel.queue_declare(queue='testqueue') # Declare a queue

        # set up subscription on the queue
        channel.basic_consume('testqueue', self.callback, auto_ack=True)

        # start consuming (blocks)
        channel.start_consuming()
        connection.close()
