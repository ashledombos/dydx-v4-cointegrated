import requests

# Configuration pour les notifications
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
EMAIL_API_URL = "https://api.emailservice.com/send"
EMAIL_API_KEY = "your-email-api-key"

def send_message(message):
    """
    Envoie un message à travers différents canaux de communication.

    :param message: Le message à envoyer.
    """
    send_slack_message(message)
    send_email("trading-bot@example.com", "Notification from Trading Bot", message)

def send_slack_message(message):
    """
    Envoie un message à un canal Slack spécifié via Webhook.

    :param message: Le message à envoyer.
    """
    data = {'text': message}
    response = requests.post(SLACK_WEBHOOK_URL, json=data)
    if response.status_code != 200:
        print(f"Failed to send Slack message: {response.text}")

def send_email(to, subject, body):
    """
    Envoie un email à l'aide d'une API de service de messagerie.

    :param to: Destinataire de l'email.
    :param subject: Sujet de l'email.
    :param body: Corps de l'email.
    """
    headers = {'Authorization': f'Bearer {EMAIL_API_KEY}'}
    data = {
        'to': to,
        'subject': subject,
        'body': body
    }
    response = requests.post(EMAIL_API_URL, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to send email: {response.text}")
