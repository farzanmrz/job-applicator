#!/usr/bin/env python3
"""
Integration test for basic workflow between Coordinator and LinkedIn Scraper.
This tests the end-to-end flow of searching for jobs and evaluating them.
"""

import os
import sys
import time
import json
import logging
import unittest
from pathlib import Path

# Adjust path to import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.messages import (
    Message, TaskMessage, StatusMessage, ErrorMessage, 
    TaskStatus, TaskPriority, create_task_message,
    serialize_message, deserialize_message
)
from agents.coordinator import CoordinatorAgent
from tools.scraping.linkedin_scraper import LinkedInScraper, JobSearchParams
from tools.preference_matching.synonym_matcher import SynonymMatcher, UserPreferences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger("WorkflowTest")


class TestLinkedInScraper:
    """
    Test implementation of LinkedIn Scraper that doesn't use actual web scraping
    but returns mock data for testing purposes.
    """
    
    def __init__(self):
        self.is_started = False
        self.is_logged_in = False
    
    def start(self):
        self.is_started = True
        return True
    
    def login(self):
        self.is_logged_in = True
        return True
    
    def stop(self):
        self.is_started = False
        self.is_logged_in = False
    
    def search_jobs(self, search_params):
        """Return mock job listings"""
        return [
            {
                "job_id": "123456789",
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "url": "https://linkedin.com/jobs/view/123456789",
                "description": "We're looking for a skilled Python developer with 5+ years of experience.",
                "employment_type": "Full-time",
                "experience_level": "Senior",
                "remote_type": "Remote"
            },
            {
                "job_id": "987654321",
                "title": "Machine Learning Engineer",
                "company": "AI Solutions",
                "location": "New York, NY",
                "url": "https://linkedin.com/jobs/view/987654321",
                "description": "Looking for ML engineers with experience in Python, TensorFlow, and PyTorch.",
                "employment_type": "Full-time",
                "experience_level": "Mid-Senior level",
                "remote_type": "Hybrid"
            }
        ]


class TestPreferenceMatcher:
    """
    Test implementation of Preference Matcher that uses simplified logic
    for testing purposes.
    """
    
    def normalize_preference(self, category, value):
        """Simple normalization for testing"""
        return value, 1.0
    
    def match_preferences_to_job(self, preferences, job_data):
        """Simple matching for testing"""
        match_score = 0.75  # Mock score
        
        return {
            "match_score": match_score,
            "matches": {
                "job_type": {
                    "preference": "Full-time",
                    "job_value": "Full-time"
                },
                "job_experience": {
                    "preference": "Senior-Level",
                    "job_value": "Senior"
                }
            },
            "mismatches": {
                "location": {
                    "preference": "Remote",
                    "job_value": "Hybrid"
                }
            }
        }


class MockAgent:
    """
    Mock agent for testing coordinator interaction.
    """
    
    def __init__(self, agent_id, coordinator):
        self.agent_id = agent_id
        self.coordinator = coordinator
        self.received_messages = []
        self.running = True
        
        # Register with coordinator
        coordinator.register_agent(agent_id, ["test_capability"])
    
    def start(self):
        """Start receiving messages"""
        import threading
        self.thread = threading.Thread(target=self._message_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop receiving messages"""
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
    
    def _message_loop(self):
        """Message receiving loop"""
        while self.running:
            # Try to receive message
            message = self.coordinator.receive_message(self.agent_id, timeout=0.1)
            
            if message:
                self.received_messages.append(message)
                
                # Process task messages
                if isinstance(message, TaskMessage):
                    # Send status update
                    self.coordinator.update_task_status(
                        message.task_id, 
                        TaskStatus.IN_PROGRESS,
                        progress=0.5,
                        details="Working on task"
                    )
                    
                    # Simulate work
                    time.sleep(0.1)
                    
                    # Complete task
                    self.coordinator.update_task_status(
                        message.task_id, 
                        TaskStatus.COMPLETED,
                        progress=1.0,
                        details="Task completed"
                    )
            
            # Short sleep to prevent tight loop
            time.sleep(0.01)


class BasicWorkflowTest(unittest.TestCase):
    """
    Test the basic workflow of the job application system:
    1. Start coordinator
    2. Register agents
    3. Search for jobs
    4. Match preferences
    5. Evaluate results
    """
    
    def setUp(self):
        """Set up test environment"""
        # Initialize coordinator
        self.coordinator = CoordinatorAgent()
        
        # Create mock agents
        self.search_agent = MockAgent("job_searcher", self.coordinator)
        self.evaluator_agent = MockAgent("job_evaluator", self.coordinator)
        
        # Initialize test components
        self.linkedin_scraper = TestLinkedInScraper()
        self.preference_matcher = TestPreferenceMatcher()
        
        # Start agents
        self.search_agent.start()
        self.evaluator_agent.start()
    
    def tearDown(self):
        """Clean up after tests"""
        # Stop agents
        self.search_agent.stop()
        self.evaluator_agent.stop()
        
        # Shutdown coordinator
        self.coordinator.shutdown()
    
    def test_job_search_workflow(self):
        """Test the job search workflow"""
        logger.info("Starting job search workflow test")
        
        # 1. Create a search task
        search_task_id = self.coordinator.create_and_assign_task(
            recipient="job_searcher",
            description="Search for Python Developer jobs",
            parameters={
                "keywords": "Python Developer",
                "location": "San Francisco, CA",
                "job_type": "Full-time",
                "max_results": 10
            }
        )
        
        self.assertIsNotNone(search_task_id, "Search task should be created")
        
        # Wait for task to be processed
        time.sleep(0.5)
        
        # Verify task was completed
        self.assertIn(search_task_id, self.coordinator.completed_tasks, 
                     "Search task should be completed")
        
        # 2. Create a mock user preferences
        test_preferences = UserPreferences(
            user_id="test_user",
            job_type=["Full-time"],
            modality=["Remote"],
            job_experience=["Senior-Level"],
            technical_skills=["Python", "Django", "Flask"]
        )
        
        # 3. Create evaluation tasks for each job
        # In a real implementation, this would use the actual jobs returned
        # from the search task
        mock_jobs = self.linkedin_scraper.search_jobs(None)
        
        for job in mock_jobs:
            eval_task_id = self.coordinator.create_and_assign_task(
                recipient="job_evaluator",
                description=f"Evaluate job match for {job['title']}",
                parameters={
                    "job_data": job,
                    "user_preferences": test_preferences.dict()
                }
            )
            
            self.assertIsNotNone(eval_task_id, "Evaluation task should be created")
        
        # Wait for tasks to be processed
        time.sleep(0.5)
        
        # 4. Verify all tasks were processed
        active_tasks = len(self.coordinator.active_tasks)
        self.assertEqual(active_tasks, 0, f"All tasks should be processed, but {active_tasks} are still active")
        
        # In a real implementation, we would verify the evaluation results
        # by checking the completed tasks and their outputs
        
        logger.info("Job search workflow test completed successfully")
    
    def test_message_serialization(self):
        """Test message serialization and deserialization"""
        # Create a task message
        task_msg = create_task_message(
            sender="test_sender",
            recipient="test_recipient",
            description="Test task",
            priority=TaskPriority.HIGH,
            parameters={"key": "value"},
            dependencies=["task1", "task2"]
        )
        
        # Serialize to JSON
        serialized = serialize_message(task_msg)
        
        # Deserialize from JSON
        deserialized = deserialize_message(serialized)
        
        # Verify fields match
        self.assertEqual(deserialized.sender, task_msg.sender)
        self.assertEqual(deserialized.recipient, task_msg.recipient)
        self.assertEqual(deserialized.description, task_msg.description)
        self.assertEqual(deserialized.priority, task_msg.priority)
        self.assertEqual(deserialized.parameters, task_msg.parameters)
        self.assertEqual(deserialized.dependencies, task_msg.dependencies)


if __name__ == "__main__":
    unittest.main()