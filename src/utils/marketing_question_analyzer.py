"""Intelligent marketing question analyzer - analyzes company data and determines what questions to ask."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class MarketingQuestionAnalyzer:
    """Analyzes company data and determines which marketing questions need to be asked."""
    
    # Field mappings: questionnaire_id -> company_data fields to check
    FIELD_MAPPINGS = {
        "company_name": ["company_name", "basic_info.company_name"],
        "product_description": ["solution", "solution.solution_description", "description"],
        "target_audience": ["target_market", "problem.target_audience", "market.target_market"]
    }
    
    def __init__(self, company_data: Dict):
        """
        Initialize the analyzer with company data.
        
        Args:
            company_data: Company data dictionary
        """
        self.company_data = company_data or {}
    
    def _get_field_value(self, field_path: str):
        """Get field value from company_data, handling nested paths."""
        parts = field_path.split('.')
        value = self.company_data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _is_meaningful_value(self, value) -> bool:
        """Check if a value is meaningful (not empty, not placeholder)."""
        if value is None:
            return False
        
        if isinstance(value, (int, float)):
            return value > 0
        
        if isinstance(value, str):
            value = value.strip().lower()
            placeholders = ['n/a', 'na', 'none', 'tbd', 'to be determined', 
                          'not available', 'unknown', '?', '...', '']
            if value in placeholders:
                return False
            return len(value) > 2
        
        if isinstance(value, list):
            return len(value) > 0
        
        if isinstance(value, dict):
            return len(value) > 0
        
        return bool(value)
    
    def get_missing_questions(self, questionnaire: List[Dict]) -> List[Dict]:
        """
        Filter questionnaire to only include questions for which data is missing.
        
        Args:
            questionnaire: Full questionnaire list
            
        Returns:
            Filtered list of questions to ask
        """
        missing_questions = []
        
        for question in questionnaire:
            question_id = question.get("id")
            
            # Check if this question has a field mapping
            if question_id in self.FIELD_MAPPINGS:
                fields_to_check = self.FIELD_MAPPINGS[question_id]
                
                # Check if any field has meaningful data
                has_data = False
                for field_path in fields_to_check:
                    value = self._get_field_value(field_path)
                    if value and self._is_meaningful_value(value):
                        has_data = True
                        logger.info(f"Found existing data for {question_id} in {field_path}")
                        break
                
                # If data exists, skip this question
                if has_data:
                    continue
            
            # Question needs to be asked
            missing_questions.append(question)
        
        return missing_questions
    
    def update_answers_with_company_data(self, answers: Dict) -> Dict:
        """
        Merge company data into answers for fields that exist.
        
        Args:
            answers: Answers dictionary from questionnaire
            
        Returns:
            Updated answers with company data merged in
        """
        updated_answers = answers.copy()
        
        for question_id, field_paths in self.FIELD_MAPPINGS.items():
            if question_id not in updated_answers:
                # Try to get value from company_data
                for field_path in field_paths:
                    value = self._get_field_value(field_path)
                    if value and self._is_meaningful_value(value):
                        # Convert nested dicts to strings if needed
                        if isinstance(value, dict):
                            value = str(value)
                        updated_answers[question_id] = value
                        logger.info(f"Auto-filled {question_id} from company_data: {field_path}")
                        break
        
        return updated_answers


