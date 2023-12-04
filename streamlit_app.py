
import requests
import json
import pandas as pd
import logging
import configparser
import argparse
import schedule
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up logging
logging.basicConfig(filename='/Users/donmenicohudson/Downloads/langchain_agent.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--langsmith_endpoint', help='The Langsmith API endpoint')
parser.add_argument('--trulens_endpoint', help='The Trulens API endpoint')
parser.add_argument('--api_key', help='The API key')
args = parser.parse_args()

# Get the API endpoints and headers from the command-line arguments or the configuration file
config = configparser.ConfigParser()
config.read('/Users/donmenicohudson/Downloads/langchain_agent.ini')
langsmith_api_endpoint = args.langsmith_endpoint or config.get('API', 'langsmith_endpoint')
trulens_api_endpoint = args.trulens_endpoint or config.get('API', 'trulens_endpoint')
headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {args.api_key or config.get('API', 'api_key')}"
}

# Define the job that will be scheduled
def job():
    try:
        # Make a GET request to the Langsmith API
        langsmith_response = requests.get(langsmith_api_endpoint, headers=headers)
        langsmith_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error making request to Langsmith API: {e}')
        langsmith_data = {}
    else:
        # Parse the Langsmith API response
        langsmith_data = langsmith_response.json()
        logging.info('Langsmith API response parsed successfully')

    try:
        # Make a GET request to the Trulens API
        trulens_response = requests.get(trulens_api_endpoint, headers=headers)
        trulens_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error making request to Trulens API: {e}')
        trulens_data = {}
    else:
        # Parse the Trulens API response
        trulens_data = trulens_response.json()
        logging.info('Trulens API response parsed successfully')

    try:
        # Combine the Langsmith and Trulens data into a single report
        report = pd.concat([pd.DataFrame(langsmith_data), pd.DataFrame(trulens_data)], ignore_index=True)
    except Exception as e:
        logging.error(f'Error combining data into report: {e}')
        report = pd.DataFrame()
    else:
        logging.info('Data combined into report successfully')

    # Define the file path
    file_path = '/Users/donmenicohudson/Downloads/report.csv'

    try:
        # Save the report as a CSV file
        report.to_csv(file_path, index=False)
    except Exception as e:
        logging.error(f'Error saving report: {e}')
    else:
        logging.info('Report saved successfully')

        # Send an email notification
        try:
            # Define the email parameters
            sender = 'sender@example.com'
            receiver = 'receiver@example.com'
            subject = 'Report saved successfully'
            body = f'The report has been saved as {file_path}.'
            server = 'smtp.example.com'
            username = 'username'
            password = 'password'

            # Create the email
            email = MIMEMultipart()
            email['From'] = sender
            email['To'] = receiver
            email['Subject'] = subject
            email.attach(MIMEText(body, 'plain'))

            # Send the email
            with smtplib.SMTP(server) as smtp:
                smtp.login(username, password)
                smtp.send_message(email)
        except Exception as e:
            logging.error(f'Error sending email: {e}')

# Schedule the job to run every hour
schedule.every(1).hours.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
