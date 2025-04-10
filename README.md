# Job Applicator: Multi-Agent Framework for Autonomous Job Search

Job Applicator is an AI-powered multi-agent system designed to automate the job search and application process. The system intelligently discovers, evaluates, and applies to job opportunities on LinkedIn that match your professional profile.

## Features

The system consists of five specialized agents:

1. **Profile Agent**: Understands your professional identity and skills
2. **Search Agent**: Discovers relevant job opportunities on LinkedIn
3. **Evaluation Agent**: Assesses job fit against your profile
4. **Application Agent**: Handles the submission process
5. **Coordinator Agent**: Orchestrates the entire system

Each agent works autonomously while collaborating through a common messaging framework.

## Standardized Preferences

The system includes a preference standardization utility that maps between variant terminology across different job portals:

- Maintains a canonical schema of job preference categories and values
- Maps portal-specific terms to standardized internal representation
- Uses string similarity matching for inexact matches
- Handles complex mappings for platform-specific implementations
- Learns from user feedback to improve matching over time

## Getting Started

### Prerequisites
- Python 3.8+
- A LinkedIn account
- Your updated resume/CV

### Installation

1. Set up the environment:
```bash
# Create and activate conda environment
conda env create -f env.yml
conda activate jobenv
```

2. For the free local LLM option (alternative to OpenAI):
   - Install Ollama from https://ollama.com/
   - Pull a model:
   ```bash
   ollama pull llama2
   ```

### Usage
Run the main application:
```bash
./runapp.sh
```

#### Using Browser-Use with Local Ollama

The application uses the browser-use package with a local Ollama LLM to interact with LinkedIn:

```python
# Create the UI agent
ui_agent = LinkedInUIAgent(agent)

# Apply preferences
result = ui_agent.apply_preferences({
    "job_type": "Full-time",
    "modality": "Remote"
})
```

This approach uses a local Llama 3 model through Ollama and doesn't require OpenAI API keys.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
[MIT License](LICENSE)