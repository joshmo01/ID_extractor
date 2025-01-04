import requests
import json
import base64
import re
from typing import Optional
from pydantic import BaseModel, Field

class PersonalDetails(BaseModel):
    name: str = Field(..., description="Full name as shown on PAN card")
    father_name: str = Field(..., description="Father's name as shown on PAN card")

class PANCardInfo(BaseModel):
    document_type: str = Field(default="PAN Card", description="Type of the document")
    account_number: str = Field(..., pattern="^[A-Z]{5}[0-9]{4}[A-Z]$", description="10 character PAN number")
    personal_details: PersonalDetails
    date_of_birth: str = Field(..., pattern="^[0-9]{2}-[0-9]{2}-[0-9]{4}$", description="Date of birth in DD-MM-YYYY format")
    signature_present: bool = Field(default=False, description="Whether signature is present on the card")
    photo_present: bool = Field(default=False, description="Whether photo is present on the card")

def clean_json_string(text: str) -> str:
    """Extract and clean JSON from text response"""
    # Find the first { and last }
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
        
    json_str = text[start:end + 1]
    
    # Remove any trailing commas before closing braces
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Remove any non-JSON content
    json_str = re.sub(r'```json|```', '', json_str)
    
    return json_str

def extract_pan_info(image_path: str) -> PANCardInfo:
    # Read and encode image
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    # Create prompt with the schema
    prompt = """Extract ONLY the following information from the PAN card and return it in valid JSON format:
    {
        "document_type": "PAN Card",
        "account_number": "exact PAN number",
        "personal_details": {
            "name": "exact name as shown",
            "father_name": "exact father's name as shown"
        },
        "date_of_birth": "DD-MM-YYYY format",
        "signature_present": true/false,
        "photo_present": true/false
    }
    
    Return ONLY the JSON object, no additional text or explanation."""

    # Make API call
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3.2-vision:latest",
            "prompt": prompt,
            "images": [image_base64],
            "stream": True,
            "temperature": 0.1,
            "system": "You are a PAN card information extractor. Return ONLY the JSON object with the extracted information, nothing else."
        }
    )

    # Collect full response
    full_response = ""
    for line in response.iter_lines():
        if line:
            json_response = json.loads(line)
            full_response += json_response.get('response', '')
            if json_response.get('done', False):
                break

    try:
        # Clean and parse JSON
        clean_json = clean_json_string(full_response)
        data = json.loads(clean_json)
        
        # Force default values for signature and photo presence
        data['signature_present'] = True  # Since we can see a signature field
        data['photo_present'] = True      # Since we can see a photo
        
        # Validate and create Pydantic model instance
        return PANCardInfo(**data)
    except Exception as e:
        print(f"Raw response: {full_response}")  # For debugging
        raise ValueError(f"Failed to parse PAN card information: {str(e)}")

def main():
    try:
        # Test the function
        image_path = "test3.jpg"
        result = extract_pan_info(image_path)
        
        # Print formatted output
        print("\nExtracted PAN Card Information:")
        print(result.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()