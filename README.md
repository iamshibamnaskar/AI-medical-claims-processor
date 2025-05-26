# Health Insurance Claim Processor

An intelligent system that processes and validates health insurance claims using AI-powered document analysis and validation.

## Overview

This system automates the processing of health insurance claims by:
1. Extracting information from uploaded PDF documents
2. Validating the extracted information across multiple document types
3. Making claim decisions based on document consistency and completeness

## Architecture

### Components

1. **FastAPI Backend**
   - Handles file uploads
   - Manages asynchronous task processing
   - Provides REST API endpoints

2. **Celery Task Queue**
   - Manages long-running document processing tasks
   - Handles background processing
   - Uses Redis as message broker

3. **AI Document Processing**
   - Uses Google's Gemini Pro Vision for document extraction
   - Implements CrewAI for multi-agent validation
   - Structured validation workflow

4. **Multi-Agent Validation System**
   - Bill Validator Agent
   - Discharge Summary Validator Agent
   - ID Card Validator Agent
   - Meta Validator Agent

### Data Flow

1. PDF Upload → FastAPI
2. FastAPI → Celery Task Queue
3. Celery → Document Extraction (Gemini)
4. Extraction Results → Validation Crew
5. Validation Results → Final Decision

## Setup

### Prerequisites

- Python 3.10+
- Redis Server
- Google Ai studio acount (for Gemini API)

### Environment Variables

Create a `.env` file:
```env
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_gemini_api_key
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd health-assignment
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A core.celery.celery.celery_app worker --pool=solo --loglevel=info
```

3. Start FastAPI server:
```bash
uvicorn main:app --reload
```

## API Endpoints

1. **Process Claim Documents**
   - `POST /v1/process/`
   - Accepts multiple PDF files
   - Returns task IDs for processing

2. **Get Processing Result**
   - `GET /v1/process/result/{task_id}`
   - Returns validation results and claim decision

## AI Implementation

### 1. Document Extraction (Gemini Pro Vision)

Used for extracting structured information from PDF documents:
- ID Card details
- Discharge Summary
- Bill information

Example Prompt:
```
You are a medical insurance claim document assistant.
You have received a PDF file that contains multiple document types inside it.
Extract the full formatted text of each of the following document types separately from the PDF:
- id card
- discharge summary
- bill

Return a JSON object with exactly these three keys: "id", "discharge", and "bill".
Each key should contain the full formatted extracted text of that document type.
```

### 2. Multi-Agent Validation (CrewAI)

Four specialized agents working together:

1. **Bill Validator Agent**
```python
bill_agent = Agent(
    role="Bill Validator",
    goal="Check the accuracy and completeness of bill documents",
    backstory="You're an expert in healthcare billing. Your task is to validate if all expected fields like hospital_name, total_amount, and date_of_service are correct and complete based on the PDF content.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    llm=llm,
)
```

2. **Meta Validator Agent**
```python
meta_validation_task = Task(
    description=(
        "You are given the combined output of three validation agents (Bill, Discharge Summary, and ID Card). "
        "Your job is to cross-check the patient names, policy details, total amount. "
        "Minor discrepancies in patient name and minor potential spelling error in the diagnosis and other fields are acceptable. "
        "Based on three outputs DECISION and your analysis (70% weight to validator decisions, 30% to your analysis), "
        "provide a claim_decision object with status and reason."
    ),
    expected_output="JSON data detailed summary report",
    tools=[],
    agent=final_validator_agent,
)
```

## Example Output

```json
{
  "documents": [
    {
      "type": "bill",
      "hospital_name": "City General Hospital",
      "total_amount": 12500,
      "date_of_service": "2024-04-10"
    },
    {
      "type": "discharge_summary",
      "patient_name": "John Doe",
      "diagnosis": "Fracture",
      "admission_date": "2024-04-01",
      "discharge_date": "2024-04-10"
    },
    {
      "type": "id_card",
      "name": "John Doe",
      "idtype": "AADHAR"
    }
  ],
  "validation": {
    "missing_documents": [],
    "discrepancies": []
  },
  "claim_decision": {
    "status": "approved",
    "reason": "All required documents present and data is consistent"
  }
}
```

## Error Handling

The system includes comprehensive error handling for:
- PDF processing errors
- AI model failures
- Validation inconsistencies
- JSON parsing errors



## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

