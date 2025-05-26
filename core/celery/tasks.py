from core.celery.celery import celery_app
from core.crew.crew import run_document_validation
import google.generativeai as genai
import tempfile
import re
import json
import os
from celery import chain

# Configure Gemini API key (ensure this is safe in production)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

@celery_app.task(name='core.celery.tasks.extract_documents_from_pdf_task', bind=True)
def extract_documents_from_pdf_task(self, file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        gemini_file = genai.upload_file(file_path)
        prompt = """
You are a medical insurance claim document assistant.
You have received a PDF file that contains multiple document types inside it.
Extract the full formatted text of each of the following document types separately from the PDF:
- id card
- discharge summary
- bill
Return a JSON object with exactly these three keys: "id", "discharge", and "bill".
Each key should contain the full formatted extracted text of that document type. and some keydatas that you should highlight them
in id
name: NAME
type: ADHAR/PAN/VOTER/other
number: unique id number on id
in dischrge
patient_name: name of the patient,
diagnosis: diagnosis thing,
admission_date: date of admission,
discharge_date: date of discharge
in bill
hospital_name: hospital name,
total_amount: total amount,
date_of_service: date of service
If a document type is not found in the PDF, return NOT FOUND for that key.
Return only valid JSON. No extra explanation or markdown formatting.
Example output:
{
  "id": "Full formatted text of the ID card here or NOT FOUND",
  "discharge": "Full formatted text of the discharge summary here or NOT FOUND",
  "bill": "Full formatted text of the bill here or NOT FOUND"
}
Return Only JSON
"""
        response = model.generate_content([prompt, gemini_file])
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.text.strip(), flags=re.IGNORECASE)
        result = json.loads(cleaned)
        
        # Clean up the temporary file
        try:
            os.remove(file_path)
        except:
            pass
            
        return result
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse JSON from model response",
            "raw_response": response.text if 'response' in locals() else "No response",
            "details": str(e)
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
            "file_path": file_path
        }

@celery_app.task(name='core.celery.tasks.run_document_validation_task', bind=True)
def run_document_validation_task(self, extraction_result):
    try:
        if isinstance(extraction_result, dict) and "error" in extraction_result:
            return extraction_result
            
        # Extract the required fields from the extraction result
        bill_text = extraction_result.get('bill', 'NOT FOUND')
        discharge_text = extraction_result.get('discharge', 'NOT FOUND')
        id_card_text = extraction_result.get('id', 'NOT FOUND')
        
        # Run the validation
        validation_result = run_document_validation(
            bill_text=bill_text,
            discharge_text=discharge_text,
            id_card_text=id_card_text
        )
        
        return validation_result
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
            "extraction_result": extraction_result
        }

def process_claim_chain(file_path):
    """Create a chain of tasks for processing a claim"""
    return chain(
        extract_documents_from_pdf_task.s(file_path),
        run_document_validation_task.s()
    ) 