import requests
import json
import base64
from markitdown import MarkItDown
from openai import OpenAI



def describe_image(image_path):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    response = requests.post('http://localhost:11434/api/generate', 
        json={
            "model": "llama3.2-vision:latest",
            "prompt": "Describe this image in detail in json format",
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


client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("test4.jpg")
print(result.text_content)

result = describe_image("test4.jpg")
print(result)
