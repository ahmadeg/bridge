from flask import Flask, request, jsonify
import openai
openai.api_key = "YOUR_API_KEY"

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    prompt = data['prompt']
    model = "text-davinci-002"
    temperature = 0.7
    max_tokens = 50
    
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return jsonify({
        "response": response.choices[0].text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
