from flask import Flask, request, jsonify
import openai
from ibm_watson import AssistantV2,AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import requests
import json
model = "text-davinci-002"
max_tokens = 70
temperature = 0.7
openai.api_key ="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"
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
    print(message_)
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
app = Flask(__name__)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message =  data['prompt']
    reposnse  = WA_Send_message(message)
    reposnse_text = reposnse['output']['generic'][0]['text']
    if reposnse_text =="Dont Understand":
        reposnse = GPT_Snd_message(message)
    else:
        reposnse = jsonify({
            "response": reposnse_text, 'source':'Watson'})

    return reposnse

if __name__ == '__main__':
    #WA_init()
    app.run(host='0.0.0.0', port=5000,debug=True)

