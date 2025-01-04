import requests
import json

response = requests.post('http://localhost:11434/api/generate', 
    json={"model": "llama3.2-vision:latest", "prompt": "What is 2+2?"},
    stream=True)

full_response = ""
for line in response.iter_lines():
    if line:
        json_response = json.loads(line)
        full_response += json_response.get('response', '')
        if json_response.get('done', False):
            break

print("Full Response:", full_response)