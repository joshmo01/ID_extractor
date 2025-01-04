import requests
import json
import base64
from markitdown import MarkItDown

class OllamaVisionClient:
   @property
   def chat(self):
       return self
       
   @property
   def completions(self):
       return self
       
   def create(self, model=None, messages=None):
       image_path = messages[0]['content']
       with open(image_path, "rb") as f:
           image_base64 = base64.b64encode(f.read()).decode()
           
       response = requests.post('http://localhost:11434/api/generate', 
           json={
               "model": "llama3.2-vision:latest",
               "prompt": "Describe this image",
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
       
       return {"choices": [{"message": {"content": full_response}}]}

client = OllamaVisionClient()
md = MarkItDown(llm_client=client, llm_model="llama3.2-vision")
result = md.convert("test3.jpg")
print(result.text_content)