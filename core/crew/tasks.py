from crewai import Task
from core.crew.agents import bill_agent, discharge_agent, id_card_agent, final_validator_agent

bill_validation_task = Task(
    description=(
        "You are given this bill text:\n\n{bill_text}\n\n"
        "Validate if it contains the hospital name, total amount, and date of service."
        " Return a structured response indicating whether each field is present and correctly formatted."
        "at the last give resulrt as DECISION:ACCEPTED/REJECTED based on the content"
        "if multiple total amount present add them ad give the sum"
        "if Nothing found in text give BILL NOT FOUND"
    ),
    expected_output="Text Status report with field-wise validation.",
    tools=[],
    agent=bill_agent,
)

discharge_summary_task = Task(
    description=(
        "You are given this discharge summary text:\n\n{discharge_text}\n\n"
        "Check for the presence and correctness of patient name, diagnosis, admission date, and discharge date."
        "at the last give resulrt as DECISION:ACCEPTED/REJECTED based on the content"
        "if Nothing found in text give DISCHARGE SUMMARY NOT FOUND"
    ),
    expected_output="Text Checklist of required fields with validation status.",
    tools=[],
    agent=discharge_agent,
)

id_card_validation_task = Task(
    description=(
        "You are given this ID card text:\n\n{id_card_text}\n\n"
        "Verify if it includes name,id_type,unique_number. Validate completeness and correctness."
        "at the last give resulrt as DECISION:ACCEPTED/REJECTED based on the content"
        "if Nothing found in text give ID CARD NOT FOUND"
    ),
    expected_output="Text Status report with field-wise validation.",
    tools=[],
    agent=id_card_agent,
)


# New meta-validation task for final reconciliation
meta_validation_task = Task(
    description=(
        "You are given the combined output of three validation agents (Bill, Discharge Summary, and ID Card). "
        "This includes all their findings and validations.\n\n"
        "{combined_results_prompt}\n\n"
        "Your job is to cross-check the patient names, policy details, total amount . Minor discrepancies in patient name and minor potential spelling error the diagnosis and other fields are acceptable"
        "and hospital name across these outputs. Identify any mismatches or inconsistencies, and provide a final validation "
        "summary highlighting both the matches and mismatches clearly."

    ),
    expected_output="JSON data detailed summary report",
    tools=[],
    agent=final_validator_agent,
)
