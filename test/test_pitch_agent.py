"""Test script for PitchAgent with sample company data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from src.data.load_company_data import load_test_company_data, format_company_data_for_pitch

# Load test company data
print("Loading test company data...")
company_data = load_test_company_data()

if not company_data:
    print("❌ Failed to load test company data")
    sys.exit(1)

print(f"✅ Loaded company data for: {company_data.get('basic_info', {}).get('company_name', 'Unknown')}")

# Format for pitch generation
print("\nFormatting company data for pitch...")
formatted_data = format_company_data_for_pitch(company_data)
print("✅ Formatted data:")
print(json.dumps(formatted_data, indent=2))

# Example: Save to user_companies folder
print("\n" + "="*80)
print("To use with PitchAgent:")
print("="*80)
print("""
# Option 1: Use formatted data (simpler)
from src.data.load_company_data import load_test_company_data, format_company_data_for_pitch
from src.agents.pitch_agent import PitchAgent
# ... initialize agent ...

company_data = load_test_company_data()
formatted = format_company_data_for_pitch(company_data)
response = agent.generate_from_details(formatted)

# Option 2: Use full company data (more context)
response = agent.generate_from_details(company_data)
""")

print("\n" + "="*80)
print("Sample company data structure:")
print("="*80)
print(f"""
Company: {company_data.get('basic_info', {}).get('company_name')}
Industry: {company_data.get('basic_info', {}).get('industry')}
Stage: {company_data.get('basic_info', {}).get('company_stage')}
Problem: {company_data.get('problem', {}).get('problem_statement', '')[:100]}...
Solution: {company_data.get('solution', {}).get('solution_description', '')[:100]}...
""")

