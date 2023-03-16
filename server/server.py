import os
import sys
import logging
import time
import re
# from datetime import datetime as dt
import datetime
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from requests import Session
from zeep import Client
from zeep.transports import Transport
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting")


def mrmsupport_bot_user_info(user_id, phone, clientPath):
    login = os.environ.get('MRMSUPPORTBOT_AUTH_LOGIN', '')
    password = os.environ.get('MRMSUPPORTBOT_AUTH_PASSWORD', '')

    session = Session()
    session.auth = HTTPBasicAuth(login, password)

    results = []
    for w in clientPath:
        client = Client(w, transport=Transport(session=session))
        logger.info('Calling user_info from: ' + str(w))
        try:
            res = client.service.user_info(user_id, phone)
            logger.info('user_info result: ' + str(res))
            # code		= res.result.code
            # message		= res.result.message
            if res and res['result']:
                results.append(str(res))
        except Exception as e:
            logger.error(str(w) + ' user_info error: ' + str(e))
    logger.info('user_info results count: ' + str(len(results)))
    return results


def main():

    test = True

    logger.info("Server started")

    if test:
        token = os.environ.get("TOKEN_TEST")
        clientPath = [
            'http://10.2.4.141/Test_MSK_MRM/ws/Telegram.1cws?wsdl',
            'http://10.2.4.141/Test_Piter_MRM/ws/Telegram.1cws?wsdl'
            ]
    else:
         token = os.environ.get("TOKEN")
         clientPath = [
            'http://10.2.4.123/productionMSK/ws/Telegram.1cws?wsdl',
            'http://10.2.4.123/productionNNOV/ws/Telegram.1cws?wsdl',
            'http://10.2.4.123/productionSPB/ws/Telegram.1cws?wsdl'
            ]
         
    calls_path = os.environ.get("CALLS_PATH")

    while True:
        # Read the list of files in the calls_path directory
        files = os.listdir(calls_path)
        # Iterate over file path
        for file in files:
            # filename sample: 2023-03-14_17-41-32_9998451900
            # extract the date and phone number from the filename
            # date, phone_number = re.findall(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(\d+)", file)[0]
            # filename sample: 2023-03-15_16-03_4952878442
            date, phone_number = re.findall(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})_(\d+)", file)[0]
            logger.info("Date: {}, Phone number: {}".format(date, phone_number))

            # If date older than a day
            # if datetime.datetime.strptime(date, "%Y-%m-%d_%H-%M-%S") < datetime.datetime.now() - datetime.timedelta(days=1):
            if datetime.datetime.strptime(date, "%Y-%m-%d_%H-%M") < datetime.datetime.now() - datetime.timedelta(days=1):
                logger.info("Date older than a day, skipping: "+file)
            else:
            
                # Get user information
                reply = '[\n'
                results = mrmsupport_bot_user_info('', phone_number, clientPath)
                
                if len(results) == 0:
                    reply = 'User not found: '+phone_number
                else:
                    reply += ',\n'.join(results)
                    reply += '\n]'
                # logger.info('Replying in '+str(message.chat.id))
                logger.info('Reply: '+reply)
                # bot.reply_to(message, reply + '\n]')

                # Send the reply to the telegram chat
                chat_id = os.environ.get("CHAT_ID")
                # Url
                url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(token, chat_id, reply)
                # Send the request
                r = requests.get(url)

            # Join the file path and file name
            file_path = os.path.join(calls_path, file)
            
            # check if file exists before attempting to remove it
            if os.path.exists(file_path):
                # remove the file
                os.remove(file_path)
                logger.info("Removed file: {}".format(file_path))
            
        time.sleep(1)


if __name__ == "__main__":
        main()
