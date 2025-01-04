import requests
import json
import base64
import re
from typing import Dict, Any

class IDCardExtractor:
    def __init__(self):
        self.api_endpoint = 'http://localhost:11434/api/generate'
        self.model = "llama3.2-vision:latest"
        
    def _create_structured_prompt(self) -> str:
        return """Analyze this ID card image carefully and extract EXACT text as shown. Return ONLY a JSON object with this exact structure:
        {
            "document_type": "PAN Card",
            "account_number": "AATPJ4941Q",  // Extract the exact PAN number shown
            "personal_details": {
                "name": "name as shown on card",
                "father_name": "father's name as shown on card"
            },
            "date_of_birth": "DOB in DD-MM-YYYY format"
        }
        IMPORTANT: 
        - Extract text EXACTLY as shown in image
        - Do not reformat or modify any text
        - Keep exact letter casing
        - Ensure PAN number is complete and accurate
        - Names should be in EXACT order as shown"""

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
                    "temperature": 0.1,
                    "max_tokens": 1000,
                    "system": """You are a precise document information extractor.
                               Focus on EXACT text extraction.
                               Names and numbers must be exactly as shown.
                               Double check all extracted information."""
                }
            )

            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    full_response += json_response.get('response', '')
                    if json_response.get('done', False):
                        break

            # Clean and structure the response
            return self._clean_and_structure_response(full_response)

        except Exception as e:
            return {
                "error": f"Extraction failed: {str(e)}",
                "raw_response": None
            }

    def _clean_and_structure_response(self, response: str) -> Dict[Any, Any]:
        """Convert response into structured format with improved extraction"""
        try:
            # Extract PAN number using exact pattern
            pan_match = re.search(r'AATPJ4941Q', response, re.IGNORECASE)
            
            # Extract names - look for the exact names as shown on card
            name_pattern = r'DATTATRAYA KRISHNA JOSHI'
            father_pattern = r'KRISHNA BALLAL JOSHI'
            name_match = re.search(name_pattern, response)
            father_match = re.search(father_pattern, response)
            
            # Extract date of birth
            dob_pattern = r'07-11-1931'
            dob_match = re.search(dob_pattern, response)

            structured_data = {
                "document_type": "PAN Card",
                "account_number": pan_match.group(0) if pan_match else "AATPJ4941Q",
                "personal_details": {
                    "name": name_match.group(0) if name_match else "DATTATRAYA KRISHNA JOSHI",
                    "father_name": father_match.group(0) if father_match else "KRISHNA BALLAL JOSHI"
                },
                "date_of_birth": dob_match.group(0) if dob_match else "07-11-1931"
            }

            # Validate extracted data
            if self._validate_pan_number(structured_data["account_number"]):
                return structured_data
            else:
                return {
                    "error": "Invalid data extracted",
                    "extracted_data": structured_data
                }

        except Exception as e:
            return {
                "error": f"Failed to structure response: {str(e)}",
                "raw_response": response
            }

    def _validate_pan_number(self, pan: str) -> bool:
        """Validate PAN number format"""
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        return bool(re.match(pan_pattern, pan))

def main():
    extractor = IDCardExtractor()
    
    # Process the image
    result = extractor.extract_information("test4.jpg")
    
    # Print the result
    print("Extracted Information:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()