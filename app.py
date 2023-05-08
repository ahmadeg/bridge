from flask import Flask, request, jsonify,make_response
import openai
from ibm_watson import AssistantV2,AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import requests
import json
import logging
import uuid
model = "text-davinci-002"
max_tokens = 70
temperature = 0.7
#openai.api_key ="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"
#openai.api_key = "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"
openai.api_key = "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"
WA_Service_instance_URL = "https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/a5f8f9a9-45f3-4758-a904-20e83e243885"
WA_Draft_Environment_ID = "5a7b9855-4a3e-4a03-9b84-27ec8667be9d"
WA_IAM_APIKEY= "1uqgw_qQJqwa7w9xZ8UmWRyodqzoXt0U4i_YpTmIAedy"
WA_Authenticator = None
WA_Assistant = None
WA_Session = None
WA_Session_ID = None
WA_version1='2019-02-28'
WA_version2 = "2018-09-20"
WA_version3 = "2021-11-27"
WA_version4 = "2021-05-13"

def WA_Send_message(message_):
    #########################
    # Open Session to send and receive messages
    #############################################
    WA_Authenticator = IAMAuthenticator(WA_IAM_APIKEY)
    WA_Assistant = AssistantV2(
        version=WA_version2,
        authenticator=WA_Authenticator)
    WA_Assistant.set_service_url(WA_Service_instance_URL)
    WA_Session = WA_Assistant.create_session(WA_Draft_Environment_ID).get_result()
    WA_Session_ID = json.dumps(WA_Session).split(':')[1][2:-2]
    # #########################
    # # Message
    # #########################
    message = WA_Assistant.message(
        WA_Draft_Environment_ID,
        WA_Session_ID,
        input={'text': message_},
        context={
            'metadata': {
                'deployment': 'myDeployment'
            }
        }).get_result()
    #########################
    # Close Session  to send and receive messages
    #########################
    WA_Assistant.delete_session(WA_Draft_Environment_ID, WA_Session_ID).get_result()
    #return json.dumps(message, indent=2)
    return message


def GPT_Snd_message(message):
    response = openai.Completion.create(
        engine=model,
        prompt=message,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return jsonify({
        "response": response.choices[0].text,'source':'GPT'})

def generate_json(self, data):
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
app = Flask(__name__)
# Configure logging
#logging.basicConfig(filename='requests.log', level=logging.INFO)
############################################


@app.route('/chat_uneeq', methods=['POST'])
def chat_uneeq():
    # Log the incoming request payload
    #logging.info('Incoming payload: %s', request.data)
    resource_uuid = str(uuid.uuid4())
    data = request.get_json()
    #message =  data['prompt']
    message = data['fm-question'] if 'fm-question' in data else None
    fmAvatar = data["fm-avatar"] if "dfm-avatar" in data else None
    session_id = fmAvatar["avatarSessionId"] if "avatarSessionId" in data else None
    sid = data["sid"] if "sid" in data else None
    response  = WA_Send_message(message)
    reposnse_text = response['output']['generic'][0]['text']
    if reposnse_text =="Dont Understand":
        response = GPT_Snd_message(message)
        reposnse_text = response.choices[0].text
    answer_body = {
        "answer": reposnse_text,
        "instructions": {}
    }

    body = {
        "answer": generate_json(answer_body),
        "matchedContext": '',
        "conversationPayload": ''
    }
    #payload  = jsonify({ "answer": {"answer":reposnse_text,"instructions":{}}, "matchedContext": "", "conversationPayload": {"platformSessionId":resource_uuid}})
    response = make_response(body)
    response.status_code = 200
    return response






@app.route('/chat', methods=['POST'])
def chat():
    # Log the incoming request payload
    #logging.info('Incoming payload: %s', request.data)
    resource_uuid = str(uuid.uuid4())
    data = request.get_json()
    #message =  data['prompt']
    message = data['fm-question']
    response  = WA_Send_message(message)
    reposnse_text = response['output']['generic'][0]['text']
    if reposnse_text =="Dont Understand":
        response = GPT_Snd_message(message)
        reposnse_text = response.choices[0].text
    payload  = jsonify({ "answer": {"answer":reposnse_text,"instructions":{}}, "matchedContext": "", "conversationPayload": {"platformSessionId":resource_uuid}})
    response = make_response(payload)
    response.status_code = 200
    return response

if __name__ == '__main__':
    #WA_init()
    app.run(host='0.0.0.0', port=5000)

