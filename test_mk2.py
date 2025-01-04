import requests
import json
import base64

def describe_image(image_path):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    response = requests.post('http://localhost:11434/api/generate', 
        json={
            "model": "llama3.2-vision:latest",
            "prompt": "Describe this image in detail",
            "images": [image_base64],
            "stream": True
        })

    full_response = ""
    for line in response.iter_lines():
        if line:
            json_response = json.loads(line)
            full_response += json_response.get('response', '')
            if json_response.get('done', False):
                break
    
    return full_response

result = describe_image("test2.jpg")
print(result)
