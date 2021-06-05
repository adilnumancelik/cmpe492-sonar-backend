import pika, os, logging

# Function to push a message to queue
'''
queue_name is the name of the queue the message will be pushed

doi_list is the list of dois to be pushed

'''
def push_to_queue(queue_name, doi_list):
    # Push the dois to fetcher queue
    logging.basicConfig()

    # Parse CLODUAMQP_URL (fallback to localhost)
    url = os.environ.get('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    params.socket_timeout = 5

    connection = pika.BlockingConnection(params) # Connect to CloudAMQP
    channel = connection.channel() # start a channel
    channel.queue_declare(queue=queue_name) # Declare a queue
    
    # send the dois
    for doi in doi_list:
        channel.basic_publish(exchange='', routing_key=queue_name, body=doi)
    
    connection.close()
