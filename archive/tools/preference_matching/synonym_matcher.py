#!/usr/bin/env python3
"""
Synonym Matcher - Tool for matching job preferences with job listings
using semantic understanding and synonym detection
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from pathlib import Path
import difflib

from pydantic import BaseModel, Field
from dotenv import load_dotenv

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("preference_matcher.log")
    ]
)

logger = logging.getLogger("PreferenceMatcher")


class PreferenceCategory(BaseModel):
    """Model for a preference category with canonical values and synonyms"""
    
    canonical_values: Dict[str, List[str]]
    synonyms: List[str] = Field(default_factory=list)


class PreferenceSchema(BaseModel):
    """Schema for job preferences"""
    
    job_type: Optional[PreferenceCategory] = None
    modality: Optional[PreferenceCategory] = None
    job_experience: Optional[PreferenceCategory] = None
    education: Optional[PreferenceCategory] = None
    industries: Optional[PreferenceCategory] = None
    job_titles: Optional[PreferenceCategory] = None
    availability: Optional[PreferenceCategory] = None
    compensation: Optional[PreferenceCategory] = None
    technical_skills: Optional[PreferenceCategory] = None
    soft_skills: Optional[PreferenceCategory] = None
    locations: Optional[PreferenceCategory] = None


class UserPreferences(BaseModel):
    """User job preferences"""
    
    user_id: str
    job_type: Optional[List[str]] = None
    modality: Optional[List[str]] = None
    job_experience: Optional[List[str]] = None
    education: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    availability: Optional[str] = None
    compensation: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    custom_preferences: Dict[str, Any] = Field(default_factory=dict)


class SynonymMatcher:
    """
    Tool for matching job preferences with job listings using synonym detection
    and semantic understanding
    """
    
    def __init__(
        self,
        schema_path: Optional[str] = None,
        db_path: Optional[str] = None,
        llm_provider: str = "anthropic",
        similarity_threshold: float = 0.8
    ):
        """
        Initialize the SynonymMatcher
        
        Args:
            schema_path: Path to preference schema JSON file
            db_path: Path to SQLite database for storing preferences
            llm_provider: LLM provider to use ('anthropic' or 'openai')
            similarity_threshold: Threshold for string similarity matching
        """
        # Load environment variables
        load_dotenv()
        
        # Set default paths if not provided
        self.schema_path = schema_path or os.path.join(
            Path(__file__).parent.parent.parent, "data", "prefschema.json")
        
        self.db_path = db_path or os.path.join(
            Path(__file__).parent.parent.parent, "db", "preferences.db")
        
        # Initialize schema
        self.schema = self._load_schema()
        
        # Initialize database
        self._init_database()
        
        # Set similarity threshold
        self.similarity_threshold = similarity_threshold
        
        # Initialize LLM client
        self.llm_provider = llm_provider
        self.llm_client = self._init_llm_client()
        
        logger.info("SynonymMatcher initialized")
    
    def _load_schema(self) -> PreferenceSchema:
        """
        Load preference schema from JSON file
        
        Returns:
            PreferenceSchema
        """
        try:
            if not os.path.exists(self.schema_path):
                logger.warning(f"Schema file not found at {self.schema_path}, using empty schema")
                return PreferenceSchema()
            
            with open(self.schema_path, 'r') as f:
                schema_data = json.load(f)
            
            # Convert JSON to PreferenceSchema
            schema_dict = {}
            for category, values in schema_data.items():
                schema_dict[category] = PreferenceCategory(**values)
            
            schema = PreferenceSchema(**schema_dict)
            logger.info(f"Loaded preference schema with {len(schema_dict)} categories")
            return schema
            
        except Exception as e:
            logger.error(f"Error loading schema from {self.schema_path}: {e}")
            return PreferenceSchema()
    
    def _init_database(self) -> None:
        """
        Initialize SQLite database for storing preferences
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create preferences table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                category TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE (user_id, category, value)
            )
            ''')
            
            # Create custom preferences table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                name TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE (user_id, name)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Initialized database at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def _init_llm_client(self) -> Any:
        """
        Initialize LLM client based on provider
        
        Returns:
            LLM client
        """
        if self.llm_provider == "anthropic" and ANTHROPIC_AVAILABLE:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found in environment variables")
                return None
            
            try:
                client = Anthropic(api_key=api_key)
                logger.info("Initialized Anthropic client")
                return client
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {e}")
                return None
        
        elif self.llm_provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
                return None
            
            try:
                openai.api_key = api_key
                logger.info("Initialized OpenAI client")
                return openai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                return None
        
        else:
            provider_name = "Anthropic" if self.llm_provider == "anthropic" else "OpenAI"
            logger.warning(f"{provider_name} client not available, semantic matching will be limited")
            return None
    
    def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """
        Save user preferences to database
        
        Args:
            preferences: UserPreferences object
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update user
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (preferences.user_id,)
            )
            
            # Delete existing preferences for this user
            cursor.execute(
                "DELETE FROM preferences WHERE user_id = ?",
                (preferences.user_id,)
            )
            
            # Insert new preferences
            for category, values in preferences.dict(exclude={"user_id", "custom_preferences"}).items():
                if values:
                    if isinstance(values, list):
                        for value in values:
                            if value:  # Only insert non-empty values
                                cursor.execute(
                                    "INSERT INTO preferences (user_id, category, value) VALUES (?, ?, ?)",
                                    (preferences.user_id, category, value)
                                )
                    else:
                        if values:  # Only insert non-empty values
                            cursor.execute(
                                "INSERT INTO preferences (user_id, category, value) VALUES (?, ?, ?)",
                                (preferences.user_id, category, values)
                            )
            
            # Handle custom preferences
            if preferences.custom_preferences:
                # Delete existing custom preferences
                cursor.execute(
                    "DELETE FROM custom_preferences WHERE user_id = ?",
                    (preferences.user_id,)
                )
                
                # Insert new custom preferences
                for name, value in preferences.custom_preferences.items():
                    # Convert non-string values to JSON
                    if not isinstance(value, str):
                        value = json.dumps(value)
                    
                    cursor.execute(
                        "INSERT INTO custom_preferences (user_id, name, value) VALUES (?, ?, ?)",
                        (preferences.user_id, name, value)
                    )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved preferences for user {preferences.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences from database
        
        Args:
            user_id: User ID
            
        Returns:
            UserPreferences or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            if not cursor.fetchone():
                logger.warning(f"User {user_id} not found")
                conn.close()
                return None
            
            # Get preferences
            cursor.execute(
                "SELECT category, value FROM preferences WHERE user_id = ?",
                (user_id,)
            )
            
            preferences_data = {}
            for category, value in cursor.fetchall():
                if category not in preferences_data:
                    if category in {"availability", "compensation"}:
                        # Single value fields
                        preferences_data[category] = value
                    else:
                        # List fields
                        preferences_data[category] = [value]
                else:
                    if isinstance(preferences_data[category], list):
                        preferences_data[category].append(value)
            
            # Get custom preferences
            cursor.execute(
                "SELECT name, value FROM custom_preferences WHERE user_id = ?",
                (user_id,)
            )
            
            custom_preferences = {}
            for name, value in cursor.fetchall():
                # Try to parse JSON values
                try:
                    custom_preferences[name] = json.loads(value)
                except json.JSONDecodeError:
                    custom_preferences[name] = value
            
            conn.close()
            
            # Create UserPreferences object
            preferences = UserPreferences(
                user_id=user_id,
                custom_preferences=custom_preferences,
                **preferences_data
            )
            
            logger.info(f"Retrieved preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Error retrieving preferences: {e}")
            return None
    
    def normalize_preference(
        self, 
        category: str, 
        value: str
    ) -> Tuple[str, float]:
        """
        Normalize a preference value to its canonical form
        
        Args:
            category: Preference category
            value: Raw preference value
            
        Returns:
            Tuple of (canonical_value, confidence)
        """
        if not hasattr(self.schema, category):
            logger.warning(f"Unknown category: {category}")
            return value, 0.0
        
        category_schema = getattr(self.schema, category)
        if not category_schema:
            logger.warning(f"No schema for category: {category}")
            return value, 0.0
        
        # Check for exact match in canonical values or their synonyms
        for canonical, synonyms in category_schema.canonical_values.items():
            if value.lower() == canonical.lower():
                return canonical, 1.0
            
            if any(value.lower() == syn.lower() for syn in synonyms):
                return canonical, 1.0
        
        # Check for fuzzy match using string similarity
        best_match = None
        best_score = 0.0
        
        # Check canonical values
        for canonical in category_schema.canonical_values.keys():
            score = difflib.SequenceMatcher(None, value.lower(), canonical.lower()).ratio()
            if score > best_score and score >= self.similarity_threshold:
                best_match = canonical
                best_score = score
        
        # Check synonyms
        for canonical, synonyms in category_schema.canonical_values.items():
            for syn in synonyms:
                score = difflib.SequenceMatcher(None, value.lower(), syn.lower()).ratio()
                if score > best_score and score >= self.similarity_threshold:
                    best_match = canonical
                    best_score = score
        
        if best_match:
            return best_match, best_score
        
        # If no good match found, try semantic matching with LLM if available
        if self.llm_client:
            semantic_match = self._semantic_match(category, value)
            if semantic_match:
                return semantic_match, 0.7  # Arbitrary confidence for semantic matches
        
        # No match found, return as is
        return value, 0.0
    
    def _semantic_match(self, category: str, value: str) -> Optional[str]:
        """
        Use LLM to semantically match a value to a canonical form
        
        Args:
            category: Preference category
            value: Raw preference value
            
        Returns:
            Canonical value or None if no match
        """
        if not self.llm_client:
            return None
        
        category_schema = getattr(self.schema, category, None)
        if not category_schema:
            return None
        
        # Create list of canonical values and their synonyms
        canonical_values = list(category_schema.canonical_values.keys())
        
        if not canonical_values:
            return None
        
        try:
            # Create prompt for LLM
            prompt = f"""
            I need to match a job preference value to its canonical form.
            
            Category: {category}
            Value to match: "{value}"
            
            Canonical values to choose from:
            {', '.join(canonical_values)}
            
            Return the EXACT canonical value that best matches, or "None" if none match well.
            Only return the matching canonical value with no explanation or additional text.
            """
            
            # Call appropriate LLM API
            if self.llm_provider == "anthropic" and isinstance(self.llm_client, Anthropic):
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=20,
                    temperature=0.0,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.content[0].text.strip()
            
            elif self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    max_tokens=10,
                    temperature=0,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.choices[0].message.content.strip()
            
            else:
                return None
            
            # Process result
            if result in canonical_values:
                logger.info(f"Semantic match for '{value}' in {category}: {result}")
                return result
            elif result.lower() == "none":
                return None
            else:
                # Try to find a close match to what the LLM returned
                for canonical in canonical_values:
                    if canonical.lower() in result.lower() or result.lower() in canonical.lower():
                        logger.info(f"Partial semantic match for '{value}' in {category}: {canonical}")
                        return canonical
                
                return None
                
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return None
    
    def match_preferences_to_job(
        self, 
        user_preferences: UserPreferences,
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Match user preferences to a job listing
        
        Args:
            user_preferences: UserPreferences object
            job_data: Job listing data
            
        Returns:
            Dict with match results
        """
        if not user_preferences or not job_data:
            return {"match_score": 0.0, "matches": {}, "mismatches": {}}
        
        matches = {}
        mismatches = {}
        match_count = 0
        total_fields = 0
        
        # Helper function to normalize text for comparison
        def normalize_text(text):
            return text.lower().strip() if isinstance(text, str) else ""
        
        # Helper function to check if two values match
        def values_match(pref_value, job_value):
            if isinstance(pref_value, list):
                # Check if any value in the list matches
                job_value_norm = normalize_text(job_value)
                return any(normalize_text(v) in job_value_norm or job_value_norm in normalize_text(v) for v in pref_value)
            else:
                # Direct comparison
                pref_norm = normalize_text(pref_value)
                job_norm = normalize_text(job_value)
                return pref_norm in job_norm or job_norm in pref_norm
        
        # Process each preference category
        for category in [
            "job_type", "modality", "job_experience", "education", 
            "industries", "job_titles", "availability", "compensation",
            "technical_skills", "soft_skills", "locations"
        ]:
            pref_value = getattr(user_preferences, category, None)
            if not pref_value:
                continue
            
            # Look for the category in job data
            # Try direct field, or search in job description
            job_value = job_data.get(category)
            if not job_value and "description" in job_data:
                # For missing fields, try to extract from description using LLM
                # This is a simplified placeholder - actual implementation would use 
                # more sophisticated extraction
                job_value = self._extract_from_description(category, job_data["description"])
            
            if job_value:
                if values_match(pref_value, job_value):
                    matches[category] = {
                        "preference": pref_value,
                        "job_value": job_value
                    }
                    match_count += 1
                else:
                    mismatches[category] = {
                        "preference": pref_value,
                        "job_value": job_value
                    }
            
            total_fields += 1
        
        # Calculate match score
        match_score = match_count / total_fields if total_fields > 0 else 0.0
        
        return {
            "match_score": match_score,
            "matches": matches,
            "mismatches": mismatches
        }
    
    def _extract_from_description(
        self, 
        category: str, 
        description: str
    ) -> Optional[str]:
        """
        Extract preference value from job description
        
        Args:
            category: Preference category
            description: Job description text
            
        Returns:
            Extracted value or None
        """
        # This is a simplified placeholder
        # A full implementation would use LLM-based extraction
        # or more sophisticated NLP techniques
        
        # Get possible values for this category
        category_schema = getattr(self.schema, category, None)
        if not category_schema:
            return None
        
        canonical_values = list(category_schema.canonical_values.keys())
        all_values = canonical_values.copy()
        
        # Add synonyms to search for
        for canonical, synonyms in category_schema.canonical_values.items():
            all_values.extend(synonyms)
        
        # Look for values in description
        for value in all_values:
            if value.lower() in description.lower():
                # Found a match, normalize to canonical form
                canonical, _ = self.normalize_preference(category, value)
                return canonical
        
        return None


def cli():
    """
    Command-line interface for the SynonymMatcher
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Preference Matcher CLI")
    parser.add_argument("--schema", help="Path to preference schema JSON file")
    parser.add_argument("--db", help="Path to SQLite database file")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic", help="LLM provider")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Normalize command
    normalize_parser = subparsers.add_parser("normalize", help="Normalize a preference value")
    normalize_parser.add_argument("category", help="Preference category")
    normalize_parser.add_argument("value", help="Preference value to normalize")
    
    # Save preferences command
    save_parser = subparsers.add_parser("save", help="Save user preferences")
    save_parser.add_argument("user_id", help="User ID")
    save_parser.add_argument("--preferences", help="Path to JSON file with preferences")
    
    # Get preferences command
    get_parser = subparsers.add_parser("get", help="Get user preferences")
    get_parser.add_argument("user_id", help="User ID")
    
    # Match command
    match_parser = subparsers.add_parser("match", help="Match preferences to job")
    match_parser.add_argument("user_id", help="User ID")
    match_parser.add_argument("job", help="Path to JSON file with job data")
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Initialize matcher
    matcher = SynonymMatcher(
        schema_path=args.schema,
        db_path=args.db,
        llm_provider=args.provider
    )
    
    if args.command == "normalize":
        canonical, confidence = matcher.normalize_preference(args.category, args.value)
        print(f"Normalized: {args.value} -> {canonical} (confidence: {confidence:.2f})")
    
    elif args.command == "save":
        if args.preferences:
            try:
                with open(args.preferences, 'r') as f:
                    preferences_data = json.load(f)
                
                preferences = UserPreferences(user_id=args.user_id, **preferences_data)
                success = matcher.save_user_preferences(preferences)
                
                if success:
                    print(f"Saved preferences for user {args.user_id}")
                else:
                    print(f"Failed to save preferences for user {args.user_id}")
                
            except Exception as e:
                print(f"Error loading preferences from {args.preferences}: {e}")
        
        else:
            print("Please provide --preferences with path to JSON file")
    
    elif args.command == "get":
        preferences = matcher.get_user_preferences(args.user_id)
        
        if preferences:
            print(f"Preferences for user {args.user_id}:")
            for category, values in preferences.dict(exclude={"user_id", "custom_preferences"}).items():
                if values:
                    print(f"  {category}: {values}")
            
            if preferences.custom_preferences:
                print("  Custom preferences:")
                for name, value in preferences.custom_preferences.items():
                    print(f"    {name}: {value}")
        else:
            print(f"No preferences found for user {args.user_id}")
    
    elif args.command == "match":
        try:
            # Load job data
            with open(args.job, 'r') as f:
                job_data = json.load(f)
            
            # Get user preferences
            preferences = matcher.get_user_preferences(args.user_id)
            
            if not preferences:
                print(f"No preferences found for user {args.user_id}")
                return
            
            # Match preferences to job
            match_results = matcher.match_preferences_to_job(preferences, job_data)
            
            print(f"Match results for user {args.user_id}:")
            print(f"Match score: {match_results['match_score']:.2f}")
            
            print("\nMatches:")
            for category, details in match_results["matches"].items():
                print(f"  {category}: {details['preference']} matches {details['job_value']}")
            
            print("\nMismatches:")
            for category, details in match_results["mismatches"].items():
                print(f"  {category}: {details['preference']} does not match {details['job_value']}")
            
        except Exception as e:
            print(f"Error matching preferences to job: {e}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()