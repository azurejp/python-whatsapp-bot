import logging
from flask import current_app, jsonify
import json
import requests

# from app.services.openai_service import generate_response
import re


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_response(response):
    # Return text in uppercase
    return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

# Define a function to handle "General" button action
def handle_general():
    version = current_app.config["VERSION"]
    phone_id = current_app.config["PHONE_NUMBER_ID"]
    # URL for the WhatsApp API
    url = f"https://graph.facebook.com/v{version}/{phone_id}/messages"
    print(url)
    # Access token for authorization
    access_token = current_app.config["ACCESS_TOKEN"]
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    print("Handling 'General' button action")

    to_phone = current_app.config["RECIPIENT_WAID"]

    data = {
    "messaging_product": "whatsapp",
    "to": f"whatsapp:{to_phone}",  # recipient's phone number
    "type": "template",
    "template": {
        "name": "surefire_options",  # template name
        "language": {
            "code": "en"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "Ganesh"},  # first variable
                    # {"type": "text", "text": "October 25, 2024"}  # second variable
                ]
            }
        ]
    }
}


# Define a function to handle "General" button action
def handle_main():
    version = current_app.config["VERSION"]
    phone_id = current_app.config["PHONE_NUMBER_ID"]
    # URL for the WhatsApp API
    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    print(url)
    # Access token for authorization
    access_token = current_app.config["ACCESS_TOKEN"]
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    print("Handling 'General' button action")

    to_phone = current_app.config["RECIPIENT_WAID"]

    data = {
    "messaging_product": "whatsapp",
    "to": f"whatsapp:{to_phone}",  # recipient's phone number
    "type": "template",
    "template": {
        "name": "main_option_selector",  # template name
        "language": {
            "code": "en"
        },
        "components": [
        ]
    }
}

    # Send the request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Print the response
    print(response.status_code)
    print(response.json())


# Define a function to handle unknown button action
def handle_unknown_button(text):
    print(f"Unknown button text: {text}")


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    logging.info(f"message: {message}")
    

    button_actions = ""
    message_body = ""
    response = ""
    button_text = ""
     # Check if the type is 'button'
    if message.get('type') == 'button':
        button_text = message['button'].get('text')
        
        if (button_text == "General"):
            handle_general()
        else:
            handle_unknown_button(button_text)

    else:
        # message_body = message["text"]["body"]
        # response = generate_response(message_body)
        # data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
        # send_message(data)
        # Get the function to execute based on the button text, or fall back to a default handler
        # action = button_actions.get(button_text, lambda: handle_unknown_button(button_text))
        # action()  # Execute the function
        handle_main()

    # TODO: implement custom function here
    
    # OpenAI Integration
    # response = generate_response(message_body, wa_id, name)
    # response = process_text_for_whatsapp(response)

    


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
