#!/usr/bin/env python3
"""
Test script for the Preference Model
"""

import os
import sys
import logging
import json
import argparse
import importlib

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Import and reload the module to ensure latest version
import classes.PrefModel
importlib.reload(classes.PrefModel)
from classes.PrefModel import PrefModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("preference_model_test")


def print_section(title):
    """Print a section title."""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def test_model(args):
    """Run tests on the Preference Model."""
    # Initialize the model
    print_section("Initializing Preference Model")
    if args.custom_schema and os.path.exists(args.custom_schema):
        model = PrefModel(schema_path=args.custom_schema)
        print(f"Model initialized with custom schema from: {args.custom_schema}")
    else:
        model = PrefModel()
        print("Model initialized with default schema")

    print("\nAvailable preference categories:")
    for category in model.get_all_canonical_categories():
        print(f"- {category}")
        if args.verbose:
            values = model.get_all_canonical_values(category)
            print(f"  Values: {', '.join(values)}")
            print(f"  Synonyms: {', '.join(model.schema[category]['synonyms'])}")
    
    # Test with example preferences
    if args.test_file and os.path.exists(args.test_file):
        print_section("Testing with Example Preferences")
        try:
            with open(args.test_file, 'r') as f:
                test_prefs = json.load(f)
                
            print("Original preferences:")
            print(json.dumps(test_prefs, indent=2))
            
            canonical_prefs = model.map_preferences(test_prefs)
            
            print("\nMapped to canonical preferences:")
            print(json.dumps(canonical_prefs, indent=2))
        except Exception as e:
            logger.error(f"Error processing test file: {str(e)}")
    
    # Test interactive mapping
    if args.interactive:
        print_section("Interactive Testing")
        try:
            while True:
                print("\nEnter a category and value to map (or 'q' to quit):")
                category_input = input("Category: ")
                if category_input.lower() == 'q':
                    break
                    
                value_input = input("Value: ")
                if value_input.lower() == 'q':
                    break
                
                # Map category
                canonical_category, category_score = model.get_canonical_category(category_input)
                if canonical_category:
                    print(f"Category '{category_input}' maps to '{canonical_category}' (Score: {category_score:.2f})")
                else:
                    print(f"Category '{category_input}' has no canonical mapping")
                    if input("Add as new category? (y/n): ").lower() == 'y':
                        model.add_category(category_input)
                        print(f"Added '{category_input}' as a new category")
                        canonical_category = category_input
                
                # Map value if we have a category
                if canonical_category:
                    canonical_value, value_score = model.get_canonical_value(canonical_category, value_input)
                    if canonical_value:
                        print(f"Value '{value_input}' maps to '{canonical_value}' in '{canonical_category}' (Score: {value_score:.2f})")
                    else:
                        print(f"Value '{value_input}' has no canonical mapping in '{canonical_category}'")
                        if input("Add as new value? (y/n): ").lower() == 'y':
                            model.add_canonical_value(canonical_category, value_input)
                            print(f"Added '{value_input}' as a new value in '{canonical_category}'")
        except KeyboardInterrupt:
            print("\nInteractive testing ended")
    
    # Save schema if requested
    if args.save_schema:
        print_section("Saving Schema")
        model.save_schema(args.save_schema)
        print(f"Schema saved to: {args.save_schema}")


def main():
    parser = argparse.ArgumentParser(description="Test Preference Model")
    parser.add_argument(
        "--custom-schema",
        help="Path to a custom schema file to load",
    )
    parser.add_argument(
        "--test-file",
        help="JSON file with preferences to test mapping",
    )
    parser.add_argument(
        "--save-schema",
        help="Path to save the final schema",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive testing mode",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information",
    )

    args = parser.parse_args()
    test_model(args)


if __name__ == "__main__":
    main()