import requests
import json
import base64
from typing import Dict, Any

class IDCardExtractor:
    def __init__(self):
        self.api_endpoint = 'http://localhost:11434/api/generate'
        self.model = "llama3.2-vision:latest"
        
    def _create_structured_prompt(self) -> str:
        return """Extract the following information from the ID card image in JSON format:
        {
            "document_type": "type of document",
            "account_number": "extracted account number",
            "personal_details": {
                "name": "full name",
                "father_name": "father's name if present"
            },
            "dates": {
                "date_of_birth": "extracted DOB",
                "date_of_issue": "issue date if present"
            },
            "additional_fields": {
                "field_name": "value"
            }
        }
        Ensure all extracted text is in the exact format as shown in the ID card."""

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def extract_information(self, image_path: str) -> Dict[Any, Any]:
        try:
            image_base64 = self._encode_image(image_path)
            
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": self._create_structured_prompt(),
                    "images": [image_base64],
                    "stream": True,
                    "temperature": 0.1,  # Lower temperature for more consistent output
                    "max_tokens": 1000
                }
            )

            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    full_response += json_response.get('response', '')
                    if json_response.get('done', False):
                        break

            # Try to parse the response as JSON
            try:
                structured_output = json.loads(full_response)
                return structured_output
            except json.JSONDecodeError:
                # If JSON parsing fails, return a formatted dictionary
                return {
                    "error": "Failed to parse JSON",
                    "raw_response": full_response
                }

        except Exception as e:
            return {
                "error": f"Extraction failed: {str(e)}",
                "raw_response": None
            }

    def validate_output(self, extracted_data: Dict[Any, Any]) -> bool:
        required_fields = [
            "document_type",
            "account_number",
            "personal_details"
        ]
        return all(field in extracted_data for field in required_fields)

def main():
    extractor = IDCardExtractor()
    
    # Process the image
    result = extractor.extract_information("test3.jpg")
    
    # Validate the output
    if extractor.validate_output(result):
        print("Structured Output:")
        print(json.dumps(result, indent=2))
    else:
        print("Error: Invalid output format")
        print(result)

if __name__ == "__main__":
    main()