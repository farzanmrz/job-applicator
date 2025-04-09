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
    
    # Initialize model with options
    model_kwargs = {}
    
    # Add custom schema if provided
    if args.custom_schema and os.path.exists(args.custom_schema):
        model_kwargs["schema_path"] = args.custom_schema
        
    # Add pending actions file if provided
    if args.pending_actions_file:
        model_kwargs["pending_actions_path"] = args.pending_actions_file
    
    # Create the model
    model = PrefModel(**model_kwargs)
    
    # Log initialization details
    if args.custom_schema and os.path.exists(args.custom_schema):
        print(f"Model initialized with custom schema from: {args.custom_schema}")
    else:
        print("Model initialized with default schema")
        
    if args.pending_actions_file:
        print(f"Using pending actions file: {args.pending_actions_file}")
        
    # Define if we'll use pending actions
    use_pending = args.use_pending

    print("\nAvailable preference categories:")
    for category in model.get_all_canonical_categories():
        print(f"- {category}")
        if args.verbose:
            values = model.get_all_canonical_values(category)
            print(f"  Values: {', '.join(values)}")
            print(f"  Synonyms: {', '.join(model.schema[category]['synonyms'])}")
            
    # Show pending actions if they exist
    if use_pending:
        pending_actions = model.get_pending_actions()
        if pending_actions:
            print_section("Pending Actions")
            for action in pending_actions:
                action_type = action.action_type
                category_action = action.is_category_action()
                
                if action_type == "Mapping":
                    if category_action:
                        print(f"[{action.id}] Map category: '{action.old_category}' -> '{action.new_category}' (score: {action.score:.2f})")
                    else:
                        print(f"[{action.id}] Map value: '{action.old_category}.{action.old_value}' -> '{action.new_category}.{action.new_value}' (score: {action.score:.2f})")
                elif action_type == "Creation":
                    if category_action:
                        print(f"[{action.id}] Create category: '{action.new_category}'")
                    else:
                        print(f"[{action.id}] Create value: '{action.new_category}.{action.new_value}'")
                elif action_type == "Rejection":
                    print(f"[{action.id}] Reject mapping: '{action.old_category}.{action.old_value}' -> '{action.new_category}.{action.new_value}' (score: {action.score:.2f})")
        else:
            print("\nNo pending actions found.")
    
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
                print("\nInteractive Testing Options:")
                print("1. Test category/value mapping")
                print("2. Manage pending actions")
                print("3. Create custom pending action")
                print("q. Quit interactive mode")
                
                choice = input("\nSelect an option: ")
                
                if choice.lower() == 'q':
                    break
                
                # Option 1: Test mapping
                if choice == '1':
                    print("\nEnter a category and value to map:")
                    category_input = input("Category: ")
                    if category_input.lower() == 'q':
                        continue
                        
                    value_input = input("Value: ")
                    if value_input.lower() == 'q':
                        continue
                    
                    # Always create pending actions in interactive mode if --use-pending is enabled
                    create_pending = use_pending
                    
                    # Map category
                    canonical_category, category_score = model.get_canonical_category(
                        category_input, create_pending=create_pending, force_pending_for_new=False
                    )
                    
                    if canonical_category:
                        print(f"Category '{category_input}' maps to '{canonical_category}' (Score: {category_score:.2f})")
                        if category_score < 1.0 and create_pending:
                            print(f"  → Created pending action for this mapping (not exact match)")
                    else:
                        print(f"Category '{category_input}' has no canonical mapping")
                        
                        # Check for near matches
                        has_near_matches = False
                        for category in model.schema.keys():
                            score = model._calculate_similarity(category_input.lower(), category.lower())
                            if score > 0.5:
                                has_near_matches = True
                                print(f"  → Found potential similar category: '{category}' (Score: {score:.2f})")
                                break
                                
                        if create_pending and has_near_matches:
                            print(f"  → Created pending action to add this as a new category")
                        elif create_pending and not has_near_matches:
                            # Auto-add if no similar categories and using pending actions
                            model.add_category(category_input)
                            print(f"  → Added '{category_input}' as a new category (no similar categories found)")
                            canonical_category = category_input
                        elif not create_pending:
                            if input("Add as new category? (y/n): ").lower() == 'y':
                                model.add_category(category_input)
                                print(f"Added '{category_input}' as a new category")
                                canonical_category = category_input
                    
                    # Map value if we have a category
                    if canonical_category:
                        canonical_value, value_score = model.get_canonical_value(
                            canonical_category, value_input, create_pending=create_pending, force_pending_for_new=False
                        )
                        
                        if canonical_value:
                            print(f"Value '{value_input}' maps to '{canonical_value}' in '{canonical_category}' (Score: {value_score:.2f})")
                            if value_score < 1.0 and create_pending:
                                print(f"  → Created pending action for this mapping (not exact match)")
                                if 0.7 <= value_score <= 0.9:
                                    print(f"  → Also created rejection action due to similarity in critical range")
                        else:
                            print(f"Value '{value_input}' has no canonical mapping in '{canonical_category}'")
                            
                            # Check for near matches
                            has_near_matches = False
                            category_values = model.schema[canonical_category]["canonical_values"]
                            for canonical_value in category_values:
                                score = model._calculate_similarity(value_input.lower(), canonical_value.lower())
                                if score > 0.5:
                                    has_near_matches = True
                                    print(f"  → Found potential similar value: '{canonical_value}' (Score: {score:.2f})")
                                    break
                                    
                            if create_pending and has_near_matches:
                                print(f"  → Created pending action to add this as a new value (near match found)")
                            elif create_pending and not has_near_matches:
                                # Auto-add if no similar values and using pending actions
                                model.add_canonical_value(canonical_category, value_input)
                                print(f"  → Added '{value_input}' as a new value (no similar values found)")
                            elif not create_pending:
                                if input("Add as new value? (y/n): ").lower() == 'y':
                                    model.add_canonical_value(canonical_category, value_input)
                                    print(f"Added '{value_input}' as a new value in '{canonical_category}'")
                
                # Option 2: Manage pending actions
                elif choice == '2':
                    pending_actions = model.get_pending_actions()
                    
                    if not pending_actions:
                        print("\nNo pending actions to manage.")
                        continue
                    
                    print("\nPending Actions:")
                    for i, action in enumerate(pending_actions):
                        action_type = action.action_type
                        category_action = action.is_category_action()
                        
                        if action_type == "Mapping":
                            if category_action:
                                print(f"{i+1}. [{action.id}] Map category: '{action.old_category}' -> '{action.new_category}' (score: {action.score:.2f})")
                            else:
                                print(f"{i+1}. [{action.id}] Map value: '{action.old_category}.{action.old_value}' -> '{action.new_category}.{action.new_value}' (score: {action.score:.2f})")
                        elif action_type == "Creation":
                            if category_action:
                                print(f"{i+1}. [{action.id}] Create category: '{action.new_category}'")
                            else:
                                print(f"{i+1}. [{action.id}] Create value: '{action.new_category}.{action.new_value}'")
                        elif action_type == "Rejection":
                            print(f"{i+1}. [{action.id}] Reject mapping: '{action.old_category}.{action.old_value}' -> '{action.new_category}.{action.new_value}' (score: {action.score:.2f})")
                    
                    action_index = input("\nSelect action to manage (number) or 'b' to go back: ")
                    
                    if action_index.lower() == 'b':
                        continue
                    
                    try:
                        action_idx = int(action_index) - 1
                        if action_idx < 0 or action_idx >= len(pending_actions):
                            print("Invalid action number.")
                            continue
                        
                        action = pending_actions[action_idx]
                        decision = input("Approve or reject this action? (a/r): ")
                        
                        if decision.lower() == 'a':
                            result = model.approve_pending_action(action.id)
                            if result:
                                print("Action approved and applied to schema.")
                            else:
                                print("Failed to approve action.")
                        elif decision.lower() == 'r':
                            result = model.reject_pending_action(action.id)
                            if result:
                                print("Action rejected and removed.")
                            else:
                                print("Failed to reject action.")
                        else:
                            print("Invalid choice.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Option 3: Create custom pending action
                elif choice == '3':
                    print("\nCreate a Custom Pending Action:")
                    
                    action_type = input("Action type (Mapping, Creation, Rejection): ")
                    if action_type not in ["Mapping", "Creation", "Rejection"]:
                        print("Invalid action type.")
                        continue
                    
                    old_category = ""
                    new_category = ""
                    old_value = ""
                    new_value = ""
                    score = 0.0
                    
                    if action_type == "Mapping" or action_type == "Rejection":
                        old_category = input("Old/source category: ")
                        if action_type == "Mapping":
                            new_category = input("New/target category: ")
                        else:
                            new_category = old_category
                        
                        is_value_action = input("Is this a value mapping? (y/n): ").lower() == 'y'
                        if is_value_action:
                            old_value = input("Old/source value: ")
                            new_value = input("New/target value: ")
                        
                        score_input = input("Similarity score (0.0-1.0): ")
                        try:
                            score = float(score_input)
                        except ValueError:
                            score = 0.0
                    
                    elif action_type == "Creation":
                        new_category = input("New category name: ")
                        is_value_action = input("Is this a value creation? (y/n): ").lower() == 'y'
                        if is_value_action:
                            new_value = input("New value name: ")
                    
                    # Add the pending action
                    action_id = model.add_pending_action(
                        action_type=action_type,
                        old_category=old_category,
                        new_category=new_category,
                        old_value=old_value,
                        new_value=new_value,
                        score=score
                    )
                    
                    print(f"Created pending action with ID: {action_id}")
                else:
                    print("Invalid option. Please try again.")
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
    parser.add_argument(
        "--use-pending",
        action="store_true",
        help="Enable pending actions for ambiguous mappings",
    )
    parser.add_argument(
        "--pending-actions-file",
        help="Path to a specific pending actions file",
    )

    args = parser.parse_args()
    test_model(args)


if __name__ == "__main__":
    main()