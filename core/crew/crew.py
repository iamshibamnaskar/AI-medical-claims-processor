from crewai import Crew, Process
import json_repair
import json
from core.crew.tasks import (
    bill_validation_task,
    discharge_summary_task,
    id_card_validation_task,
    meta_validation_task
)
from core.crew.agents import (
    bill_agent,
    discharge_agent,
    id_card_agent,
    final_validator_agent
)

def run_document_validation(bill_text: str, discharge_text: str, id_card_text: str) -> dict:
    # Step 1: Run individual validations
    initial_crew = Crew(
        agents=[bill_agent, discharge_agent, id_card_agent],
        tasks=[bill_validation_task, discharge_summary_task, id_card_validation_task],
        process=Process.sequential,
        verbose=False  # you can make verbose param if you want
    )

    initial_results = initial_crew.kickoff(inputs={
        "bill_text": bill_text,
        "discharge_text": discharge_text,
        "id_card_text": id_card_text
    })

    # Build combined prompt for meta validation
    combined_results_prompt = f"""
You are the Meta Validator agent. You have the following outputs from individual document validators:

Bill Validator output:
{bill_validation_task.output}

Discharge Summary Validator output:
{discharge_summary_task.output}

ID Card Validator output:
{id_card_validation_task.output}

Your task:
1. Extract relevant key fields from each document type and structure them in a JSON array called "documents". Each document should be an object with a "type" key and its extracted fields. For example:

{{
  "documents": [
    {{
      "type": "bill",
      "hospital_name": "ABC Hospital",
      "total_amount": 12500,
      "date_of_service": "2024-04-10"
    }},
    {{
      "type": "discharge_summary",
      "patient_name": "John Doe",
      "diagnosis": "Fracture",
      "admission_date": "2024-04-01",
      "discharge_date": "2024-04-10"
    }},
    {{
      "type": "id_card",
      "name": "john Doe"
      "idtype": "ADHAR/VOTER/PAN/PASSPORT"
    }}
  ],
  "validation": {{
    "missing_documents": [],
    "discrepancies": [
    {{
      "field" "field of discrepancies",
      "description": "description of the discrepancies"
    }}
    ]
  }},
  "claim_decision": {{
    "status": "approved",
    "reason": "All required documents present and data is consistent"
  }}
}}

2. Identify if any required document types (bill, discharge_summary, id_card) are missing and list them in "missing_documents".

3. Cross-check the structured output for missing data or inconsistencies from the required fields

4. check name is common across documents.

4. Based on three outputs DECISION and  your analysis the three Decisions gets 70% priority and your analysis gets 30% priority (if you dont find any severe reson to change outputs decision dont change), provide a "claim_decision" object with:
  - "status": either "approved" or "rejected"
  - "reason": a short explanation for the decision

Return only a valid JSON matching the format above. Do not include explanations, markdown, or any other text.
"""

    # Step 2: Run meta validation
    meta_crew = Crew(
        agents=[final_validator_agent],
        tasks=[meta_validation_task],
        process=Process.sequential,
        verbose=False
    )

    final_result = meta_crew.kickoff(inputs={
        "combined_results_prompt": combined_results_prompt
    })

    # Return the final meta-validation output as dict (or string if you prefer)
    

    try:
        # Step 1: Repair JSON string
        repaired_json = json_repair.repair_json(str(final_result))
        # Step 2: Parse it into a Python dict
        result_dict = json.loads(repaired_json)
    except Exception as e:
        print("⚠️ Error parsing final_result:", e)
        result_dict = {"error": "Invalid JSON format in final result", "raw": final_result}

    return result_dict
