#!/usr/bin/env python3

import json
import os
import sys
import time
import uuid
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from classes.PrefModel import PrefModel, PendingAction


def test_prefmodel_schema_structure():
    model = PrefModel()
    schema = model.schema

    # Assert it's a dict
    assert isinstance(schema, dict)

    # Assert that expected keys exist
    assert "job_type" in schema
    assert "modality" in schema
    assert "job_experience" in schema
    
    # Test category structure
    assert "canonical_values" in schema["job_type"]
    assert "synonyms" in schema["job_type"]
    
    # Test mapping functions
    job_type, score = model.get_canonical_category("Employment Type")
    assert job_type == "job_type"
    
    job_value, score = model.get_canonical_value("job_type", "Full Time")
    assert job_value == "Full-time"
    
    # Test preference mapping
    test_prefs = {
        "Employment Type": "full-time",
        "Location Type": "remote"
    }
    canonical_prefs = model.map_preferences(test_prefs)
    assert "job_type" in canonical_prefs
    
    print("Schema structure tests passed!")


def test_pending_actions():
    # Create a temporary file for testing pending actions
    tmp_dir = Path(os.path.dirname(__file__)) / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    pending_actions_path = tmp_dir / "test_pending_actions.json"
    
    try:
        # Initialize model with custom pending actions path
        model = PrefModel(pending_actions_path=str(pending_actions_path))
        
        # Test 1: Adding pending actions
        print("Testing adding pending actions...")
        
        # Add a pending mapping action (category)
        mapping_id = model.add_pending_action(
            action_type="Mapping",
            old_category="job_type",
            new_category="Job Status",
            score=0.85
        )
        
        # Add a pending mapping action (value)
        value_mapping_id = model.add_pending_action(
            action_type="Mapping",
            old_category="job_type",
            new_category="job_type",
            old_value="Full-time",
            new_value="Permanent",
            score=0.78
        )
        
        # Add a pending creation action (category)
        creation_id = model.add_pending_action(
            action_type="Creation",
            new_category="Certification Requirements"
        )
        
        # Test 2: Getting pending actions
        print("Testing retrieving pending actions...")
        actions = model.get_pending_actions()
        assert len(actions) == 3, f"Expected 3 pending actions, got {len(actions)}"
        
        # Test 3: Check is_category_action
        category_actions = [a for a in actions if a.is_category_action()]
        assert len(category_actions) == 2, f"Expected 2 category actions, got {len(category_actions)}"
        
        # Test 4: Approving a pending action
        print("Testing approving pending actions...")
        # First, confirm that 'Job Status' is not in schema synonyms
        job_type_synonyms = model.schema["job_type"]["synonyms"]
        assert "Job Status" not in job_type_synonyms, "Job Status should not be in job_type synonyms yet"
        
        # Approve the mapping
        result = model.approve_pending_action(mapping_id)
        assert result, "Action approval should return True"
        
        # Check if synonym was added
        job_type_synonyms = model.schema["job_type"]["synonyms"]
        assert "Job Status" in job_type_synonyms, "Job Status should now be in job_type synonyms"
        
        # Test 5: Rejecting a pending action
        print("Testing rejecting pending actions...")
        # Get remaining actions count
        actions_before = len(model.get_pending_actions())
        
        # Reject an action
        result = model.reject_pending_action(value_mapping_id)
        assert result, "Action rejection should return True"
        
        # Check if action was removed
        actions_after = len(model.get_pending_actions())
        assert actions_after == actions_before - 1, f"Expected {actions_before-1} actions, got {actions_after}"
        
        # Test 6: Test creating pending actions during mapping
        print("Testing automatic pending action creation...")
        
        # Try to map something with create_pending=True
        category, score = model.get_canonical_category("Work Contract", create_pending=True)
        
        # Check that a new pending action was created
        new_actions = [a for a in model.get_pending_actions() 
                      if a.new_category == "Work Contract"]
        assert len(new_actions) > 0, "Should have created a pending action for 'Work Contract'"
        
        print("Pending action tests passed!")
        
    finally:
        # Clean up
        if pending_actions_path.exists():
            pending_actions_path.unlink()
        if tmp_dir.exists():
            tmp_dir.rmdir()


def run_all_tests():
    test_prefmodel_schema_structure()
    test_pending_actions()
    print("All tests passed!")


if __name__ == "__main__":
    run_all_tests()