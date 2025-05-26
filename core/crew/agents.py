from crewai import Agent
from dotenv import load_dotenv
load_dotenv()
from crewai.llm import LLM
import os

llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    provider="google",
    temperature=0.5,
    verbose=True
)


bill_agent = Agent(
    role="Bill Validator",
    goal="Check the accuracy and completeness of bill documents",
    backstory="You're an expert in healthcare billing. Your task is to validate if all expected fields like hospital_name, total_amount, and date_of_service are correct and complete based on the PDF content.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    llm=llm,
)

discharge_agent = Agent(
    role="Discharge Summary Validator",
    goal="Ensure discharge summaries have proper structure and required fields",
    backstory="You're a specialist in medical discharge processes. Validate diagnosis, admission and discharge dates, and patient names for completeness and correctness.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    llm=llm,
)

id_card_agent = Agent(
    role="ID Card Validator",
    goal="Verify that ID card documents contain all necessary personal and policy information",
    backstory="You're an insurance expert focused on validating patient identity and policy metadata in ID card documents.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    llm=llm,
)

final_validator_agent = Agent(
    role="Meta Validator",
    goal="Compare and reconcile multiple validator opinions and produce a unified decision",
    backstory="You're an experienced reviewer skilled at resolving conflicting data across healthcare documents by evaluating the outputs of other agents.",
    llm=llm,
    memory=False,
    verbose=True,
    allow_delegation=False
)
