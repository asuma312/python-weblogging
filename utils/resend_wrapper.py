from flask import current_app
import requests

def send_email(email_destinatario, assunto, html_email):
    apikey = current_app.config['RESEND_APIKEY']
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": current_app.config['RESEND_EMAIL'],
        "to": [email_destinatario],
        "subject": assunto,
        "html": html_email
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending e-mail: {e}")