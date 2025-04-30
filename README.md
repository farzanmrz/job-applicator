# Job Applicator: Autonomous Job Application System

An autonomous job application system using MCP (Model Context Protocol) for structured agent communication.

## Project Structure

```
JOB-APPLICATOR/
├── agents/                 # All MCP-based agents here
│   ├── coordinator.py
│   ├── profile_manager.py
│   ├── job_searcher.py
│   ├── job_evaluator.py
│   ├── application_agent.py
│   └── tracker_agent.py
│
├── tools/                  # Practical tool modules
│   ├── scraping/
│   │   ├── linkedin_scraper.py
│   │   └── indeed_scraper.py
│   │
│   ├── profile/
│   │   ├── resume_parser.py
│   │   ├── linkedin_profile_tool.py
│   │   └── github_profile_tool.py
│   │
│   ├── applications/
│   │   ├── form_submission.py
│   │   ├── doc_customizer.py
│   │   └── company_info.py
│   │
│   └── preference_matching/
│       └── synonym_matcher.py
│
├── mcp/                    # MCP message structure and utilities
│   ├── __init__.py
│   └── messages.py
│
├── data/                   # Your existing JSON schemas and prefs (kept intact)
│   ├── prefschema.json
│   ├── prefsaved.json
│   ├── creds.json
│   └── browser_state/
│
├── db/                     # SQLite database file(s)
│   └── preferences.db
│
├── docs/                   # Existing documentation
│   └── plan.docx
│
├── frontend/               # Future frontend updates (Streamlit)
│   └── app.py
│
├── utils/                  # Utility/helper functions and shared code
│   ├── __init__.py
│   └── common.py
│
├── tests/                  # Unit and integration tests
│   └── test_workflow.py
│
├── scripts/                # Shell scripts to run components
│   └── run_app.sh
│
├── env.yml                 # Existing environment setup
└── LICENSE                 # License file
```

## Overview

This project is a modular, autonomous job application system built around the Model Context Protocol (MCP) for structured agent communication. It uses specialized agents and tools to automate various aspects of the job search and application process.

### Core Components

1. **MCP Message Structure** - Foundation for agent communication using Pydantic models
2. **Coordinator Agent** - Central orchestrator that manages task distribution and workflow
3. **LinkedIn Job Scraper** - Tool for extracting job listings from LinkedIn
4. **Preference Matcher** - Tool for matching job requirements with user preferences

## Getting Started

### Prerequisites

- Python 3.11+
- Conda environment manager

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/farzanmrz/job-applicator.git
   cd job-applicator
   ```

2. Create and activate the Conda environment:
   ```
   conda env create -f env.yml
   conda activate jobenv
   ```

3. Set up your credentials:
   - Create a `data/creds.json` file with your LinkedIn credentials:
     ```json
     {
       "linkedin": {
         "username": "your_username",
         "password": "your_password"
       }
     }
     ```

### Usage

Use the provided shell script to run various components:

```bash
# Start the coordinator agent
./scripts/run_app.sh coordinator

# Run the LinkedIn scraper
./scripts/run_app.sh linkedin search --keywords "Python Developer" --location "San Francisco"

# Manage user preferences
./scripts/run_app.sh preferences save user123 --preferences user_prefs.json

# Run tests
./scripts/run_app.sh test workflow
```

## Development

### Phase 1 Implementation (Current)

The current implementation focuses on Phase 1 components:

1. **MCP Message Structure** - Defined in `mcp/messages.py`
2. **Coordinator Agent** - Implemented in `agents/coordinator.py`
3. **LinkedIn Job Scraper** - Implemented in `tools/scraping/linkedin_scraper.py`
4. **Preference Matcher** - Implemented in `tools/preference_matching/synonym_matcher.py`
5. **Basic Integration Testing** - Implemented in `tests/test_workflow.py`

### Future Phases

- Phase 2: Enhanced Profile Integration
- Phase 3: Semantic Job Evaluation
- Phase 4: Automated Application Generation
- Phase 5: Multi-user Scalability
- Phase 6: Real-time Frontend Dashboard

Please refer to `docs/plan.txt` for the complete implementation plan.

## License

This project is licensed under the [MIT License](LICENSE).