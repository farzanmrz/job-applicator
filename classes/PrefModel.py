"""
Utility for standardizing job search preferences across different platforms.
Maps variant terminology to canonical preferences.
"""

import os
import json
import logging
import importlib
import uuid
import time
from typing import Dict, List, Optional, Tuple, Any
from difflib import SequenceMatcher
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PendingAction:
    """Represents a pending action that requires user approval."""
    id: str                  # Unique identifier for the action
    action_type: str         # "Mapping", "Rejection", "Creation"
    old_category: str        # Original/matched category
    new_category: str        # New/input category
    old_value: str           # Original/matched value
    new_value: str           # New/input value
    score: float             # Similarity score if applicable
    timestamp: float         # When the action was created
    
    def is_category_action(self) -> bool:
        """Check if this action is related to a category (not a value)."""
        return not self.old_value and not self.new_value

class PrefModel:
    """
    Utility for standardizing job search preferences across different platforms.
    
    This class maintains a canonical schema of job preference categories and their
    values, and provides methods to map variant terms to their canonical equivalents.
    """
    
    def __init__(self, schema_path: Optional[str] = None, 
                 similarity_threshold: float = 0.8,
                 pending_actions_path: Optional[str] = None,
                 auto_save: bool = True):
        """
        Initialize the preference model with a default or custom schema.
        
        Args:
            schema_path: Optional path to a JSON schema file
            similarity_threshold: Threshold for considering string similarity matches
            pending_actions_path: Optional path to store pending actions
            auto_save: Whether to automatically save schema changes back to the schema file
        """
        self.similarity_threshold = similarity_threshold
        self.schema = {}
        self.auto_save = auto_save
        
        # Set up pending actions storage
        if pending_actions_path:
            self.pending_actions_file = pending_actions_path
        else:
            self.pending_actions_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "pending_actions.json"
            )
        
        # Initialize pending actions
        self.pending_actions = []
        self._load_pending_actions()
        
        # Determine the default schema path
        self.default_schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "data", "prefschema.json"
        )
        
        # Set the active schema path
        self.active_schema_path = schema_path if schema_path else self.default_schema_path
        
        # Try to load the default schema
        if os.path.exists(self.default_schema_path):
            self.load_schema(self.default_schema_path)
        else:
            logger.warning(f"Default schema not found at {self.default_schema_path}")
            
        # Load custom schema if provided (overrides default)
        if schema_path and os.path.exists(schema_path):
            self.load_schema(schema_path)
            self.active_schema_path = schema_path
        
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
    
    def _auto_save_schema(self) -> None:
        """
        Automatically save schema if auto_save is enabled.
        Uses the active schema path that was loaded or provided during initialization.
        Also updates prefsaved.json to include any new categories.
        """
        if self.auto_save and hasattr(self, 'active_schema_path'):
            # Save schema
            self.save_schema(self.active_schema_path)
            
            # Update prefsaved.json with new categories
            self._update_prefsaved_json()
    
    def _update_prefsaved_json(self) -> None:
        """
        Update prefsaved.json to include new categories from the schema.
        New categories are added with empty values to ensure all schema 
        categories are represented in the user preferences.
        """
        # Determine the prefsaved.json path
        prefsaved_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "prefsaved.json"
        )
        
        if not os.path.exists(prefsaved_path):
            logger.warning(f"prefsaved.json not found at {prefsaved_path}")
            return
            
        try:
            # Load current preferences
            with open(prefsaved_path, 'r') as f:
                preferences = json.load(f)
                
            # Check for missing categories and add them
            modified = False
            for category in self.schema.keys():
                if category not in preferences:
                    # Add the category with an empty value
                    # Determine if category typically holds a list or single value
                    # Most preferences are lists, except a few like education
                    if category in ["education", "availability", "compensation"]:
                        preferences[category] = ""
                    else:
                        preferences[category] = []
                    modified = True
                    logger.info(f"Added new category '{category}' to prefsaved.json")
            
            # Save preferences if modified
            if modified:
                with open(prefsaved_path, 'w') as f:
                    json.dump(preferences, f, indent=2)
                    logger.info(f"Updated prefsaved.json with new categories")
        except Exception as e:
            logger.error(f"Error updating prefsaved.json: {str(e)}")
    
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
    
    def get_canonical_category(self, variant: str, create_pending: bool = False, 
                             force_pending_for_new: bool = False) -> Tuple[Optional[str], float]:
        """
        Get the canonical category name when given a variant.
        
        Args:
            variant: A potential variant of a category name
            create_pending: If True, creates a pending action for ambiguous mappings
            force_pending_for_new: If True, all new categories go to pending actions,
                                  otherwise only create pending actions for near matches
            
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
        
        # If we found a match based on similarity but it's not exact, create a pending action
        if create_pending and best_match and best_score < 1.0:
            # Create pending mapping action
            self.add_pending_action(
                action_type="Mapping",
                old_category=best_match,
                new_category=variant,
                score=best_score
            )
        
        # If no match found, only create a pending action if forced or if there's a low similarity
        elif create_pending and not best_match:
            # Only create a pending action if explicitly requested or if there are potential
            # near matches below the similarity threshold that might warrant review
            has_near_matches = False
            for category in self.schema.keys():
                score = self._calculate_similarity(normalized_variant, category)
                if score > 0.5:  # Check for marginally similar categories
                    has_near_matches = True
                    break
            
            if force_pending_for_new or has_near_matches:
                self.add_pending_action(
                    action_type="Creation",
                    new_category=variant
                )
            
        return best_match, best_score
    
    def get_canonical_value(self, category: str, variant: str, create_pending: bool = False,
                           force_pending_for_new: bool = False) -> Tuple[Optional[str], float]:
        """
        Get the canonical value when given a variant within a category.
        
        Args:
            category: The category to search in (canonical or variant)
            variant: A potential variant of a value
            create_pending: If True, creates a pending action for ambiguous mappings
            force_pending_for_new: If True, all new values go to pending actions,
                                  otherwise only create pending actions for near matches
            
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
        
        # If we found a match based on similarity but it's not exact, create a pending action
        if create_pending and best_match and best_score < 1.0:
            # Create pending mapping action
            self.add_pending_action(
                action_type="Mapping",
                old_category=canonical_category,
                new_category=canonical_category,
                old_value=best_match,
                new_value=variant,
                score=best_score
            )
            
            # For values with high similarity but possible mismatch (like "Female" and "Male")
            # If the score is between 0.7 and 0.9, also consider it a possible rejection
            if 0.7 <= best_score <= 0.9:
                self.add_pending_action(
                    action_type="Rejection",
                    old_category=canonical_category,
                    new_category=canonical_category,
                    old_value=best_match,
                    new_value=variant,
                    score=best_score
                )
        
        # If no match found, check if we need to create a pending action
        elif create_pending and not best_match:
            # Check for marginally similar values that might warrant review
            has_near_matches = False
            for canonical_value in category_values.keys():
                score = self._calculate_similarity(normalized_variant, canonical_value)
                if score > 0.5:  # Check for marginally similar values
                    has_near_matches = True
                    break
            
            if force_pending_for_new or has_near_matches:
                self.add_pending_action(
                    action_type="Creation",
                    new_category=canonical_category,
                    new_value=variant
                )
            
        return best_match, best_score
    
    def add_category(self, canonical_name: str, synonyms: List[str] = None, create_pending: bool = False) -> None:
        """
        Add a new preference category to the schema.
        
        Args:
            canonical_name: The canonical name for the new category
            synonyms: List of synonyms for this category
            create_pending: If True, creates a pending action instead of directly applying
        """
        if canonical_name in self.schema:
            logger.warning(f"Category '{canonical_name}' already exists in schema")
            return
        
        if create_pending:
            self.add_pending_action(
                action_type="Creation",
                new_category=canonical_name
            )
            return
        
        self.schema[canonical_name] = {
            "canonical_values": {},
            "synonyms": synonyms or []
        }
        logger.info(f"Added new category '{canonical_name}' to schema")
        
        # Auto-save changes
        self._auto_save_schema()
    
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
        
        # Auto-save changes
        self._auto_save_schema()
        return True
    
    def add_canonical_value(self, category: str, value: str, variants: List[str] = None, create_pending: bool = False) -> bool:
        """
        Add a new canonical value to a category.
        
        Args:
            category: The category (canonical or variant) to add to
            value: New canonical value
            variants: List of variant terms for this value
            create_pending: If True, creates a pending action instead of directly applying
            
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
        
        if create_pending:
            self.add_pending_action(
                action_type="Creation",
                new_category=canonical_category,
                new_value=value
            )
            return True
            
        self.schema[canonical_category]["canonical_values"][value] = variants or []
        logger.info(f"Added value '{value}' to category '{canonical_category}'")
        
        # Auto-save changes
        self._auto_save_schema()
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
        
        # Auto-save changes
        self._auto_save_schema()
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
    
    def _load_pending_actions(self) -> None:
        """Load pending actions from the JSON file."""
        try:
            if os.path.exists(self.pending_actions_file):
                with open(self.pending_actions_file, 'r') as f:
                    actions_data = json.load(f)
                    
                    # Convert dict representations to PendingAction objects
                    self.pending_actions = [
                        PendingAction(**action) for action in actions_data
                    ]
                    logger.info(f"Loaded {len(self.pending_actions)} pending actions")
            else:
                self.pending_actions = []
        except Exception as e:
            logger.error(f"Error loading pending actions: {str(e)}")
            self.pending_actions = []
    
    def _save_pending_actions(self) -> None:
        """Save pending actions to the JSON file."""
        try:
            directory = os.path.dirname(self.pending_actions_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            # Convert PendingAction objects to dicts
            actions_data = [action.__dict__ for action in self.pending_actions]
            
            with open(self.pending_actions_file, 'w') as f:
                json.dump(actions_data, f, indent=2)
                logger.info(f"Saved {len(self.pending_actions)} pending actions")
        except Exception as e:
            logger.error(f"Error saving pending actions: {str(e)}")
    
    def add_pending_action(self, 
                          action_type: str,
                          old_category: str = "",
                          new_category: str = "",
                          old_value: str = "",
                          new_value: str = "",
                          score: float = 0.0) -> str:
        """
        Add a new pending action that requires user approval.
        
        Args:
            action_type: Type of action ("Mapping", "Rejection", "Creation")
            old_category: Original/matched category
            new_category: New/input category
            old_value: Original/matched value
            new_value: New/input value
            score: Similarity score if applicable
            
        Returns:
            The ID of the created pending action
        """
        action_id = str(uuid.uuid4())
        
        action = PendingAction(
            id=action_id,
            action_type=action_type,
            old_category=old_category,
            new_category=new_category,
            old_value=old_value,
            new_value=new_value,
            score=score,
            timestamp=time.time()
        )
        
        self.pending_actions.append(action)
        self._save_pending_actions()
        
        logger.info(f"Added pending {action_type} action: {old_category}.{old_value} -> {new_category}.{new_value}")
        return action_id
    
    def get_pending_actions(self) -> List[PendingAction]:
        """Get all pending actions that require user approval."""
        return self.pending_actions
    
    def approve_pending_action(self, action_id: str) -> bool:
        """
        Approve a pending action and apply it to the schema.
        
        Args:
            action_id: ID of the pending action to approve
            
        Returns:
            True if approval was successful, False otherwise
        """
        # Find the action
        action = next((a for a in self.pending_actions if a.id == action_id), None)
        if not action:
            logger.error(f"Pending action not found: {action_id}")
            return False
        
        try:
            if action.action_type == "Mapping":
                # Apply the mapping
                if action.is_category_action():
                    # Category mapping
                    if action.old_category not in self.schema:
                        self.add_category(action.old_category)
                    
                    self.add_category_synonym(action.old_category, action.new_category)
                else:
                    # Value mapping
                    if action.old_category not in self.schema:
                        self.add_category(action.old_category)
                    
                    canonical_values = self.get_all_canonical_values(action.old_category)
                    if action.old_value not in canonical_values:
                        self.add_canonical_value(action.old_category, action.old_value)
                    
                    self.add_value_variant(action.old_category, action.old_value, action.new_value)
            
            elif action.action_type == "Creation":
                # Create new category or value
                if action.is_category_action():
                    # New category
                    self.add_category(action.new_category)
                else:
                    # New value
                    if action.new_category not in self.schema:
                        self.add_category(action.new_category)
                    
                    self.add_canonical_value(action.new_category, action.new_value)
            
            # Remove the action after approval
            self.pending_actions = [a for a in self.pending_actions if a.id != action_id]
            self._save_pending_actions()
            
            logger.info(f"Approved pending action: {action_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error approving action {action_id}: {str(e)}")
            return False
    
    def reject_pending_action(self, action_id: str) -> bool:
        """
        Reject a pending action.
        
        Args:
            action_id: ID of the pending action to reject
            
        Returns:
            True if rejection was successful, False otherwise
        """
        # Find and remove the action
        action = next((a for a in self.pending_actions if a.id == action_id), None)
        if not action:
            logger.error(f"Pending action not found: {action_id}")
            return False
        
        self.pending_actions = [a for a in self.pending_actions if a.id != action_id]
        self._save_pending_actions()
        
        logger.info(f"Rejected pending action: {action_id}")
        return True
    
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