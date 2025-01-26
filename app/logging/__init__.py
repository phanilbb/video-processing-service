import logging

class Logging:

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,  # You can change this to INFO or ERROR as needed
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),  # Logs to the console
                logging.FileHandler('app.log')  # Logs to a file
            ]
        )
