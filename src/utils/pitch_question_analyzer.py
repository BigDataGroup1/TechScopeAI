"""Intelligent pitch question analyzer - analyzes company data and determines what questions to ask."""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PitchQuestionAnalyzer:
    """Analyzes company data and determines which pitch questions need to be asked."""
    
    # Comprehensive pitch questions mapped to company_data fields
    PITCH_QUESTIONS = [
        {
            "id": "company_one_sentence",
            "question": "What is the company and what do you do in one sentence?",
            "fields_to_check": ["company_name", "description", "solution"],
            "priority": "high",
            "category": "basics"
        },
        {
            "id": "exact_customer",
            "question": "Who exactly is the customer?",
            "fields_to_check": ["target_market", "target_audience"],
            "priority": "high",
            "category": "market"
        },
        {
            "id": "customer_pain",
            "question": "What pain are they experiencing?",
            "fields_to_check": ["problem", "problem_statement"],
            "priority": "high",
            "category": "problem"
        },
        {
            "id": "why_painful_enough",
            "question": "Why is this painful enough to pay for?",
            "fields_to_check": ["problem"],  # Needs more depth
            "priority": "medium",
            "category": "problem"
        },
        {
            "id": "solution_10x",
            "question": "How is your solution 10× better?",
            "fields_to_check": ["unique_value_proposition", "competitive_advantage"],
            "priority": "high",
            "category": "solution"
        },
        {
            "id": "why_not_solved",
            "question": "Why hasn't this been solved already?",
            "fields_to_check": ["competitive_advantage", "unique_value_proposition"],
            "priority": "medium",
            "category": "solution"
        },
        {
            "id": "how_make_money",
            "question": "How do you make money?",
            "fields_to_check": ["business_model", "revenue_model"],
            "priority": "high",
            "category": "business"
        },
        {
            "id": "how_big_realistically",
            "question": "How big can this realistically get?",
            "fields_to_check": ["market_size", "tam", "sam", "som"],
            "priority": "high",
            "category": "market"
        },
        {
            "id": "competitors",
            "question": "Who are your competitors?",
            "fields_to_check": ["competitors", "competitive_landscape"],
            "priority": "high",
            "category": "competition"
        },
        {
            "id": "why_you_win",
            "question": "Why will you win?",
            "fields_to_check": ["competitive_advantage", "unique_value_proposition", "moat"],
            "priority": "high",
            "category": "competition"
        },
        {
            "id": "what_proof",
            "question": "What proof do you have?",
            "fields_to_check": ["traction", "revenue", "customers", "mrr", "validation"],
            "priority": "high",
            "category": "traction"
        },
        {
            "id": "team_credible",
            "question": "Why is your team credible?",
            "fields_to_check": ["team", "founders", "team_background"],
            "priority": "medium",
            "category": "team"
        },
        {
            "id": "what_need_next",
            "question": "What do you need next?",
            "fields_to_check": ["funding_goal", "use_of_funds", "next_milestones"],
            "priority": "medium",
            "category": "funding"
        },
        {
            "id": "problem_who",
            "question": "What problem are you solving, and who has this problem?",
            "fields_to_check": ["problem", "target_market"],
            "priority": "high",
            "category": "problem"
        },
        {
            "id": "why_painful_urgent",
            "question": "Why is this problem painful, urgent, and worth solving now?",
            "fields_to_check": ["problem"],  # Needs urgency/importance context
            "priority": "high",
            "category": "problem"
        },
        {
            "id": "solution_high_level",
            "question": "How does your solution work at a high level?",
            "fields_to_check": ["solution", "solution_description", "key_features"],
            "priority": "high",
            "category": "solution"
        },
        {
            "id": "solution_better_alternatives",
            "question": "Why is your solution better than existing alternatives?",
            "fields_to_check": ["competitive_advantage", "unique_value_proposition"],
            "priority": "high",
            "category": "solution"
        },
        {
            "id": "product_looks_like",
            "question": "What does the product actually look like or how is it used?",
            "fields_to_check": ["key_features", "solution", "product_description"],
            "priority": "medium",
            "category": "product"
        },
        {
            "id": "target_customer_market_size",
            "question": "Who is the target customer and how big is the market?",
            "fields_to_check": ["target_market", "market_size", "tam", "sam"],
            "priority": "high",
            "category": "market"
        },
        {
            "id": "traction_validation",
            "question": "What traction or validation do you have so far?",
            "fields_to_check": ["traction", "revenue", "customers", "mrr", "validation", "metrics"],
            "priority": "high",
            "category": "traction"
        },
        {
            "id": "differentiation",
            "question": "Who are the competitors and how do you differentiate?",
            "fields_to_check": ["competitors", "competitive_advantage"],
            "priority": "high",
            "category": "competition"
        },
        {
            "id": "acquire_grow_customers",
            "question": "How will you acquire and grow customers?",
            "fields_to_check": ["go_to_market", "customer_acquisition", "growth_strategy"],
            "priority": "medium",
            "category": "growth"
        },
        {
            "id": "team_uniquely_suited",
            "question": "Why is your team uniquely suited to solve this problem?",
            "fields_to_check": ["team", "founders", "team_background"],
            "priority": "medium",
            "category": "team"
        },
        {
            "id": "key_assumptions_risks",
            "question": "What are the key assumptions or risks?",
            "fields_to_check": ["risks", "assumptions", "challenges"],
            "priority": "low",
            "category": "risks"
        },
        {
            "id": "near_term_roadmap",
            "question": "What is your near-term roadmap or next milestone?",
            "fields_to_check": ["roadmap", "next_milestones", "use_of_funds"],
            "priority": "medium",
            "category": "future"
        },
        {
            "id": "what_asking_for",
            "question": "What are you asking for and what will it enable?",
            "fields_to_check": ["funding_goal", "use_of_funds"],
            "priority": "high",
            "category": "funding"
        }
    ]
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze_company_data(self, company_data: Dict) -> Tuple[List[Dict], Dict]:
        """
        Analyze company data and determine which questions need to be asked.
        
        Args:
            company_data: Company data dictionary (can be formatted or raw)
            
        Returns:
            Tuple of (questions_to_ask, existing_data_summary)
        """
        questions_to_ask = []
        existing_data = {}
        
        # Flatten nested company_data for easier checking
        flattened_data = self._flatten_company_data(company_data)
        
        for question_config in self.PITCH_QUESTIONS:
            question_id = question_config["id"]
            fields_to_check = question_config["fields_to_check"]
            
            # Check if any of the fields have meaningful data
            has_data = False
            found_data = None
            
            for field in fields_to_check:
                value = flattened_data.get(field, '')
                if value and self._is_meaningful_value(value):
                    has_data = True
                    found_data = value
                    break
            
            # Also check nested structures
            if not has_data:
                # Check in common nested structures
                for key in ['basic_info', 'problem', 'solution', 'market', 'traction', 'funding', 'team']:
                    if key in company_data and isinstance(company_data[key], dict):
                        for field in fields_to_check:
                            value = company_data[key].get(field, '')
                            if value and self._is_meaningful_value(value):
                                has_data = True
                                found_data = value
                                break
                    if has_data:
                        break
            
            if has_data:
                # Data exists, store it
                existing_data[question_id] = {
                    "value": found_data,
                    "question": question_config["question"]
                }
            else:
                # Need to ask this question
                questions_to_ask.append(question_config)
        
        # Sort questions by priority (high -> medium -> low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        questions_to_ask.sort(key=lambda q: priority_order.get(q["priority"], 3))
        
        return questions_to_ask, existing_data
    
    def _flatten_company_data(self, company_data: Dict) -> Dict:
        """Flatten nested company data structure for easier field checking."""
        flattened = {}
        
        # Direct fields
        for key, value in company_data.items():
            if not isinstance(value, (dict, list)):
                flattened[key] = value
            elif isinstance(value, dict):
                # Flatten nested dict
                for nested_key, nested_value in value.items():
                    if not isinstance(nested_value, (dict, list)):
                        flattened[nested_key] = nested_value
                        # Also add with prefix
                        flattened[f"{key}_{nested_key}"] = nested_value
        
        return flattened
    
    def _is_meaningful_value(self, value) -> bool:
        """Check if a value is meaningful (not empty, not placeholder)."""
        if value is None:
            return False
        
        if isinstance(value, (int, float)):
            return value > 0
        
        if isinstance(value, str):
            value = value.strip().lower()
            # Check for common placeholder values
            placeholders = ['n/a', 'na', 'none', 'tbd', 'to be determined', 
                          'not available', 'unknown', '?', '...', '']
            if value in placeholders:
                return False
            # Must have some length
            return len(value) > 3
        
        if isinstance(value, list):
            return len(value) > 0
        
        return bool(value)
    
    def get_contextual_message(self, question_config: Dict, existing_data: Dict) -> str:
        """
        Get a contextual message when a question has partial data.
        
        Args:
            question_config: Question configuration
            existing_data: Dictionary of existing data
            
        Returns:
            Contextual message string
        """
        question_id = question_config["id"]
        
        # Check if we have related data
        related_fields = question_config.get("fields_to_check", [])
        
        # Generate contextual message
        if existing_data:
            return f"💡 **Understanding your concept better...** I see some information about this, but I'd like to dive deeper."
        else:
            return "🎯 **Let's build your pitch together...**"
    
    def merge_answers_with_company_data(self, company_data: Dict, answers: Dict) -> Dict:
        """
        Merge questionnaire answers into company data.
        
        Args:
            company_data: Original company data
            answers: Answers from questionnaire
            
        Returns:
            Merged company data dictionary
        """
        merged = company_data.copy() if company_data else {}
        
        # Map question IDs to company_data fields
        question_field_mapping = {
            "company_one_sentence": ("description", "company_description"),
            "exact_customer": ("target_market", "target_audience"),
            "customer_pain": ("problem", "problem_statement"),
            "why_painful_enough": ("problem_urgency", "problem_importance"),
            "solution_10x": ("unique_value_proposition", "competitive_advantage"),
            "why_not_solved": ("competitive_advantage", "market_gap"),
            "how_make_money": ("business_model", "revenue_model"),
            "how_big_realistically": ("market_size", "market_potential"),
            "competitors": ("competitors", "competitive_landscape"),
            "why_you_win": ("competitive_advantage", "differentiation"),
            "what_proof": ("traction", "validation"),
            "team_credible": ("team_background", "founders"),
            "what_need_next": ("use_of_funds", "funding_goal"),
            "problem_who": ("problem", "target_market"),
            "why_painful_urgent": ("problem_urgency", "problem_importance"),
            "solution_high_level": ("solution", "solution_description"),
            "solution_better_alternatives": ("competitive_advantage", "differentiation"),
            "product_looks_like": ("product_description", "key_features"),
            "target_customer_market_size": ("target_market", "market_size"),
            "traction_validation": ("traction", "validation"),
            "differentiation": ("competitive_advantage", "differentiation"),
            "acquire_grow_customers": ("go_to_market", "growth_strategy"),
            "team_uniquely_suited": ("team_background", "founders"),
            "key_assumptions_risks": ("risks", "assumptions"),
            "near_term_roadmap": ("roadmap", "next_milestones"),
            "what_asking_for": ("funding_goal", "use_of_funds")
        }
        
        for question_id, answer in answers.items():
            if question_id in question_field_mapping:
                fields = question_field_mapping[question_id]
                # Use first field, or try both
                primary_field = fields[0]
                
                # Try to put in appropriate structure
                if primary_field in ["problem", "solution", "target_market"]:
                    if "problem" in primary_field and "problem" not in merged:
                        merged["problem"] = {}
                    if "solution" in primary_field and "solution" not in merged:
                        merged["solution"] = {}
                    if "target_market" == primary_field and "market" not in merged:
                        merged["market"] = {}
                
                # Set the value
                if isinstance(merged.get(primary_field.split('_')[0]), dict):
                    # Nested structure
                    nested_key = primary_field.split('_', 1)[1] if '_' in primary_field else primary_field
                    merged[primary_field.split('_')[0]][nested_key] = answer
                else:
                    # Flat structure
                    merged[primary_field] = answer
        
        return merged

