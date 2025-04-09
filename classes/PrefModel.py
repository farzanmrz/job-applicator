"""
Utility for standardizing job search preferences across different platforms.
Maps variant terminology to canonical preferences.
"""

import os
import json
import logging
import importlib
from typing import Dict, List, Optional, Tuple, Any
from difflib import SequenceMatcher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrefModel:
    """
    Utility for standardizing job search preferences across different platforms.
    
    This class maintains a canonical schema of job preference categories and their
    values, and provides methods to map variant terms to their canonical equivalents.
    """
    
    def __init__(self, schema_path: Optional[str] = None, 
                 similarity_threshold: float = 0.8):
        """
        Initialize the preference model with a default or custom schema.
        
        Args:
            schema_path: Optional path to a JSON schema file
            similarity_threshold: Threshold for considering string similarity matches
        """
        self.similarity_threshold = similarity_threshold
        
        # Default canonical preference schema
        self.schema = {
            # Employment type (full-time, part-time, etc.)
            "employment_type": {
                "canonical_values": {
                    "full_time": ["Full-Time", "Full Time", "Regular", "Permanent"],
                    "part_time": ["Part-Time", "Part Time", "Casual"],
                    "contract": ["Contract", "Temporary", "Fixed Term"],
                    "internship": ["Internship", "Intern", "Trainee"],
                    "freelance": ["Freelance", "Self-Employed", "Independent Contractor"]
                },
                "synonyms": ["Job Type", "Employment Status", "Work Type", "Position Type"]
            },
            
            # Location type (remote, on-site, hybrid)
            "location_type": {
                "canonical_values": {
                    "remote": ["Remote", "Work from Home", "Virtual", "Telecommute"],
                    "on_site": ["On-Site", "On Site", "In-Office", "In Office"],
                    "hybrid": ["Hybrid", "Flexible Location", "Remote/On-Site"]
                },
                "synonyms": ["Work Location", "Work Mode", "Work Environment", "Work Setting", "Modality"]
            },
            
            # Experience level
            "experience_level": {
                "canonical_values": {
                    "entry_level": ["Entry-Level", "Entry Level", "Junior", "Beginner"],
                    "mid_level": ["Mid-Level", "Mid Level", "Intermediate", "Experienced"],
                    "senior_level": ["Senior-Level", "Senior Level", "Advanced", "Expert"],
                    "executive": ["Executive", "Leadership", "C-Level", "Director"]
                },
                "synonyms": ["Experience", "Job Experience", "Seniority", "Career Level"]
            },
            
            # Education level
            "education_level": {
                "canonical_values": {
                    "high_school": ["High School", "Secondary Education", "GED"],
                    "associate": ["Associate's Degree", "Associate Degree", "Technical Degree"],
                    "bachelor": ["Bachelor's Degree", "Bachelor Degree", "Undergraduate Degree"],
                    "master": ["Master's Degree", "Master Degree", "Graduate Degree"],
                    "doctorate": ["Doctorate", "PhD", "Doctoral Degree"]
                },
                "synonyms": ["Education", "Degree", "Academic Qualification", "Academic Requirements"]
            },
            
            # Industry
            "industry": {
                "canonical_values": {
                    "technology": ["Technology", "IT", "Information Technology", "Tech", "Software"],
                    "healthcare": ["Healthcare", "Health Care", "Medical", "Health Services"],
                    "finance": ["Finance", "Financial Services", "Banking", "Investment"],
                    "education": ["Education", "Academic", "Teaching", "E-Learning"],
                    "manufacturing": ["Manufacturing", "Production", "Industrial"]
                },
                "synonyms": ["Industry Sector", "Business Sector", "Field", "Sector"]
            },
            
            # Job function/category
            "job_function": {
                "canonical_values": {
                    "engineering": ["Engineering", "Development", "Software Engineering"],
                    "data_science": ["Data Science", "Analytics", "Data Analysis"],
                    "product": ["Product Management", "Product Development", "Product"],
                    "design": ["Design", "UX", "UI", "User Experience", "Graphic Design"],
                    "marketing": ["Marketing", "Digital Marketing", "Advertising"],
                    "sales": ["Sales", "Business Development", "Account Management"],
                    "operations": ["Operations", "Business Operations", "Supply Chain"]
                },
                "synonyms": ["Job Function", "Department", "Role Category", "Job Category"]
            },
            
            # Compensation
            "compensation": {
                "canonical_values": {
                    "hourly": ["Hourly", "Hourly Rate", "Per Hour"],
                    "salary": ["Salary", "Annual Salary", "Yearly", "Fixed Salary"],
                    "commission": ["Commission", "Commission-Based", "Performance-Based"]
                },
                "synonyms": ["Compensation", "Pay", "Salary Type", "Remuneration", "Wage Type"]
            }
        }
        
        # Load custom schema if provided
        if schema_path and os.path.exists(schema_path):
            self.load_schema(schema_path)
        
        # Cache for storing computed similarities to avoid redundant calculations
        self._similarity_cache = {}
            
    def load_schema(self, file_path: str) -> None:
        """
        Load schema from a JSON file.
        
        Args:
            file_path: Path to the JSON schema file
        """
        try:
            with open(file_path, 'r') as f:
                custom_schema = json.load(f)
                self.schema = custom_schema
                logger.info(f"Loaded custom schema from {file_path}")
        except Exception as e:
            logger.error(f"Error loading schema from {file_path}: {str(e)}")
            logger.info("Using default schema")
            
    def save_schema(self, file_path: str) -> None:
        """
        Save the current schema to a JSON file.
        
        Args:
            file_path: Path to save the JSON schema file
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w') as f:
                json.dump(self.schema, f, indent=2)
                logger.info(f"Saved schema to {file_path}")
        except Exception as e:
            logger.error(f"Error saving schema to {file_path}: {str(e)}")
    
    def _calculate_similarity(self, string1: str, string2: str) -> float:
        """
        Calculate string similarity using SequenceMatcher.
        
        Args:
            string1: First string
            string2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        # Normalize strings for better matching
        s1 = string1.lower()
        s2 = string2.lower()
        
        # Check cache first
        cache_key = (s1, s2) if s1 < s2 else (s2, s1)
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # Calculate similarity
        similarity = SequenceMatcher(None, s1, s2).ratio()
        
        # Store in cache
        self._similarity_cache[cache_key] = similarity
        
        return similarity
    
    def get_canonical_category(self, variant: str) -> Tuple[Optional[str], float]:
        """
        Get the canonical category name when given a variant.
        
        Args:
            variant: A potential variant of a category name
            
        Returns:
            Tuple of (canonical_category, confidence_score)
            Returns (None, 0.0) if no match found
        """
        # Direct match check
        normalized_variant = variant.lower()
        
        for category, details in self.schema.items():
            # Exact match with canonical name
            if normalized_variant == category.lower():
                return category, 1.0
            
            # Check synonyms list
            for synonym in details.get("synonyms", []):
                if normalized_variant == synonym.lower():
                    return category, 1.0
        
        # Similarity-based matching if no exact match
        best_match = None
        best_score = 0.0
        
        for category, details in self.schema.items():
            # Check similarity with canonical name
            score = self._calculate_similarity(normalized_variant, category)
            if score > best_score and score >= self.similarity_threshold:
                best_match = category
                best_score = score
            
            # Check similarity with synonyms
            for synonym in details.get("synonyms", []):
                score = self._calculate_similarity(normalized_variant, synonym)
                if score > best_score and score >= self.similarity_threshold:
                    best_match = category
                    best_score = score
        
        return best_match, best_score
    
    def get_canonical_value(self, category: str, variant: str) -> Tuple[Optional[str], float]:
        """
        Get the canonical value when given a variant within a category.
        
        Args:
            category: The category to search in (canonical or variant)
            variant: A potential variant of a value
            
        Returns:
            Tuple of (canonical_value, confidence_score)
            Returns (None, 0.0) if no match found
        """
        # First, ensure we have the canonical category
        canonical_category, category_score = self.get_canonical_category(category)
        
        if not canonical_category or canonical_category not in self.schema:
            return None, 0.0
        
        # Normalize the variant
        normalized_variant = variant.lower()
        
        # Direct match check
        category_values = self.schema[canonical_category]["canonical_values"]
        
        for canonical_value, variants in category_values.items():
            # Check direct match with canonical value
            if normalized_variant == canonical_value.lower():
                return canonical_value, 1.0
            
            # Check variants list
            for var in variants:
                if normalized_variant == var.lower():
                    return canonical_value, 1.0
        
        # Similarity-based matching if no exact match
        best_match = None
        best_score = 0.0
        
        for canonical_value, variants in category_values.items():
            # Check similarity with canonical value
            score = self._calculate_similarity(normalized_variant, canonical_value)
            if score > best_score and score >= self.similarity_threshold:
                best_match = canonical_value
                best_score = score
            
            # Check similarity with variants
            for var in variants:
                score = self._calculate_similarity(normalized_variant, var)
                if score > best_score and score >= self.similarity_threshold:
                    best_match = canonical_value
                    best_score = score
        
        return best_match, best_score
    
    def add_category(self, canonical_name: str, synonyms: List[str] = None) -> None:
        """
        Add a new preference category to the schema.
        
        Args:
            canonical_name: The canonical name for the new category
            synonyms: List of synonyms for this category
        """
        if canonical_name in self.schema:
            logger.warning(f"Category '{canonical_name}' already exists in schema")
            return
        
        self.schema[canonical_name] = {
            "canonical_values": {},
            "synonyms": synonyms or []
        }
        logger.info(f"Added new category '{canonical_name}' to schema")
    
    def add_category_synonym(self, category: str, synonym: str) -> bool:
        """
        Add a new synonym to an existing category.
        
        Args:
            category: The category (canonical or variant)
            synonym: New synonym to add
            
        Returns:
            Boolean indicating success
        """
        canonical_category, _ = self.get_canonical_category(category)
        
        if not canonical_category:
            logger.error(f"Cannot add synonym. Category '{category}' not found")
            return False
        
        if "synonyms" not in self.schema[canonical_category]:
            self.schema[canonical_category]["synonyms"] = []
            
        if synonym.lower() in [s.lower() for s in self.schema[canonical_category]["synonyms"]]:
            logger.warning(f"Synonym '{synonym}' already exists for category '{canonical_category}'")
            return False
            
        self.schema[canonical_category]["synonyms"].append(synonym)
        logger.info(f"Added synonym '{synonym}' to category '{canonical_category}'")
        return True
    
    def add_canonical_value(self, category: str, value: str, variants: List[str] = None) -> bool:
        """
        Add a new canonical value to a category.
        
        Args:
            category: The category (canonical or variant) to add to
            value: New canonical value
            variants: List of variant terms for this value
            
        Returns:
            Boolean indicating success
        """
        canonical_category, _ = self.get_canonical_category(category)
        
        if not canonical_category:
            logger.error(f"Cannot add value. Category '{category}' not found")
            return False
            
        if "canonical_values" not in self.schema[canonical_category]:
            self.schema[canonical_category]["canonical_values"] = {}
            
        if value in self.schema[canonical_category]["canonical_values"]:
            logger.warning(f"Value '{value}' already exists in category '{canonical_category}'")
            return False
            
        self.schema[canonical_category]["canonical_values"][value] = variants or []
        logger.info(f"Added value '{value}' to category '{canonical_category}'")
        return True
    
    def add_value_variant(self, category: str, value: str, variant: str) -> bool:
        """
        Add a new variant to an existing canonical value.
        
        Args:
            category: The category (canonical or variant)
            value: The canonical value to add variant to
            variant: New variant to add
            
        Returns:
            Boolean indicating success
        """
        canonical_category, _ = self.get_canonical_category(category)
        
        if not canonical_category:
            logger.error(f"Cannot add variant. Category '{category}' not found")
            return False
            
        canonical_value, _ = self.get_canonical_value(canonical_category, value)
        
        if not canonical_value:
            logger.error(f"Cannot add variant. Value '{value}' not found in '{canonical_category}'")
            return False
        
        values_dict = self.schema[canonical_category]["canonical_values"]
        
        if variant.lower() in [v.lower() for v in values_dict[canonical_value]]:
            logger.warning(f"Variant '{variant}' already exists for '{canonical_value}'")
            return False
            
        values_dict[canonical_value].append(variant)
        logger.info(f"Added variant '{variant}' to '{canonical_value}' in '{canonical_category}'")
        return True
    
    def get_all_canonical_categories(self) -> List[str]:
        """
        Get a list of all canonical category names.
        
        Returns:
            List of canonical category names
        """
        return list(self.schema.keys())
    
    def get_all_canonical_values(self, category: str) -> List[str]:
        """
        Get a list of all canonical values for a category.
        
        Args:
            category: The category (canonical or variant)
            
        Returns:
            List of canonical values
        """
        canonical_category, _ = self.get_canonical_category(category)
        
        if not canonical_category:
            logger.error(f"Category '{category}' not found")
            return []
            
        return list(self.schema[canonical_category]["canonical_values"].keys())
    
    def get_value_variants(self, category: str, value: str) -> List[str]:
        """
        Get all variants for a specific canonical value.
        
        Args:
            category: The category (canonical or variant)
            value: The canonical value
            
        Returns:
            List of variants for the value
        """
        canonical_category, _ = self.get_canonical_category(category)
        
        if not canonical_category:
            logger.error(f"Category '{category}' not found")
            return []
            
        canonical_value, _ = self.get_canonical_value(canonical_category, value)
        
        if not canonical_value:
            logger.error(f"Value '{value}' not found in '{canonical_category}'")
            return []
            
        return self.schema[canonical_category]["canonical_values"][canonical_value]
    
    def update_from_user_feedback(self, category_variant: str, value_variant: str, 
                                  correct_category: str, correct_value: str) -> None:
        """
        Update the model based on user feedback for improved matching.
        
        Args:
            category_variant: The category variant that was incorrectly matched
            value_variant: The value variant that was incorrectly matched
            correct_category: The correct canonical category
            correct_value: The correct canonical value
        """
        # Ensure the correct category exists
        if correct_category not in self.schema:
            self.add_category(correct_category)
            
        # Add category synonym if needed
        canonical_category, category_score = self.get_canonical_category(category_variant)
        if canonical_category != correct_category:
            self.add_category_synonym(correct_category, category_variant)
            
        # Ensure the correct value exists
        canonical_values = self.get_all_canonical_values(correct_category)
        if correct_value not in canonical_values:
            self.add_canonical_value(correct_category, correct_value)
            
        # Add value variant
        self.add_value_variant(correct_category, correct_value, value_variant)
        
        logger.info(f"Updated model based on feedback: '{category_variant}.{value_variant}' " 
                   f"-> '{correct_category}.{correct_value}'")
    
    def map_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a dictionary of preferences to their canonical equivalents.
        
        Args:
            preferences: Dictionary of preferences in non-canonical form
            
        Returns:
            Dictionary with canonical categories and values
        """
        canonical_prefs = {}
        
        for category, values in preferences.items():
            canonical_category, category_score = self.get_canonical_category(category)
            
            if not canonical_category:
                # Keep original if no mapping found
                canonical_prefs[category] = values
                continue
                
            # Handle different value types (str, list, etc.)
            if isinstance(values, list):
                canonical_values = []
                for value in values:
                    if isinstance(value, str):
                        can_value, value_score = self.get_canonical_value(canonical_category, value)
                        if can_value:
                            canonical_values.append(can_value)
                        else:
                            canonical_values.append(value)  # Keep original if no mapping
                canonical_prefs[canonical_category] = canonical_values
            elif isinstance(values, str) and values:
                can_value, value_score = self.get_canonical_value(canonical_category, values)
                if can_value:
                    canonical_prefs[canonical_category] = can_value
                else:
                    canonical_prefs[canonical_category] = values
            else:
                # For other types, keep as is
                canonical_prefs[canonical_category] = values
                
        return canonical_prefs