import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_slack_notification(message):
    """
    Send a notification to Slack if SLACK_TOKEN and SLACK_CHANNEL are configured.
    Falls back to logging if Slack is not configured.
    """
    slack_token = os.getenv('SLACK_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL')
    
    if not slack_token or not slack_channel:
        logging.warning(f"Slack notification not sent (missing configuration): {message}")
        return
    
    try:
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=slack_channel, text=message)
        logging.info(f"Slack notification sent: {message}")
    except SlackApiError as e:
        logging.error(f"Error sending Slack notification: {e}")
