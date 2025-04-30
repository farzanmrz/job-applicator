# Autonomous Multi-Agent Job Application System - Technical Plan (v3)

## 1. Project Vision

This project aims to develop an intelligent, autonomous system leveraging a multi-agent architecture and the Message Control Protocol (MCP) to automate the job search and application process. The core vision is to create a network of specialized AI agents capable of discovering relevant job opportunities, managing a user's professional profile, evaluating job fit, and streamlining the application process across various platforms with minimal human intervention. The system is designed for background operation, providing a seamless experience for the user.

## 2. System Architecture

The system employs a three-tier agent hierarchy facilitated by the Message Control Protocol (MCP) for structured communication:

1.  **Coordinator Agent:** The top-level agent responsible for orchestrating the overall workflow, managing high-level task allocation, and serving as the central communication hub via MCP.
2.  **Manager Agents:** Middle-tier agents overseeing specific functional domains (e.g., Job Search, Profile Management, Application Processing). They receive tasks from the Coordinator, break them down into subtasks, delegate to Worker Agents, aggregate results, and report back.
3.  **Worker Agents:** Foundation-level agents performing specialized, tool-based tasks by interfacing with specific external services or data sources (e.g., searching LinkedIn, parsing resumes, interacting with job application forms).

This architecture promotes modularity, specialization, and efficient information flow.

## 3. Core Modules and Agent Responsibilities (Current Focus)

While the long-term vision includes comprehensive Profile Management and Application Processing domains, the current implementation focuses on establishing the Job Search domain.

*   **Coordinator Agent:** (Conceptual) Oversees the entire process.
*   **Job Search Manager Agent:** (Conceptual) Manages the job discovery process, delegating tasks to relevant search workers.
*   **LinkedIn Search Worker Agent (`SrchWrkrLkdn`):** (Partially Implemented) A specialized worker agent responsible for all LinkedIn-related operations.
    *   **Responsibilities:** Authenticating with LinkedIn, executing job searches based on criteria received from the Job Search Manager, parsing job listing data, applying basic filtering, and returning structured results.

## 4. Communication Protocol (MCP)

The Message Control Protocol (MCP) serves as the backbone for inter-agent communication.
*   Standardized JSON-based message templates ensure consistent data exchange.
*   Defines communication patterns for task delegation, status updates, and result reporting between Coordinator, Manager, and Worker agents.
*   The MCP framework is implemented, providing the necessary infrastructure for agent interaction.

## 5. Current Status and Immediate Focus

*   **MCP Framework:** Implemented, enabling standardized agent communication.
*   **Base Agent Class (`AgtBase`):** Implemented, providing a common foundation and identification system (type, hierarchy, unique ID) for all agents.
*   **`SrchWrkrLkdn` Agent:** Initial structure implemented with proper identification.
*   **Immediate Task:** Implement LinkedIn authentication functionality within the `SrchWrkrLkdn` agent. This involves:
    *   Reading credentials securely from `data/usr_creds.json`.
    *   Using Playwright to automate the LinkedIn login process.
    *   Maintaining the authenticated session state for subsequent actions.
    *   This authentication step is critical, enabling all further LinkedIn-based functionalities.

## 6. Updated Implementation Plan (Grounded in Current Progress)

This plan focuses on incrementally building out the capabilities of the `SrchWrkrLkdn` agent within the established framework.

*   **Phase 1: LinkedIn Authentication (Current Focus)**
    *   **Goal:** Enable `SrchWrkrLkdn` to securely authenticate with LinkedIn.
    *   **Tasks:** Implement credential reading, Playwright login automation, session state management.
    *   **Success Criteria:** Agent can successfully log into LinkedIn using stored credentials and maintain a valid session.

*   **Phase 2: LinkedIn Job Search Execution & Parsing**
    *   **Goal:** Enable `SrchWrkrLkdn` to perform job searches and extract data.
    *   **Tasks:** Implement logic to receive search criteria via MCP, construct LinkedIn search queries, execute searches using the authenticated session, scrape/parse job listing details (title, company, location, description URL, etc.).
    *   **Success Criteria:** Agent can execute searches based on input criteria and return structured, raw job listing data in JSON format.

*   **Phase 3: Basic Job Evaluation & Filtering**
    *   **Goal:** Implement initial filtering based on user preferences.
    *   **Tasks:** Integrate with a basic preference model (e.g., keywords, location from `data/usr_prefs.json`), apply filters to the parsed job listings. (Note: Advanced semantic evaluation using AI models is a future enhancement).
    *   **Success Criteria:** Agent can filter the raw job list based on predefined user preferences.

*   **Phase 4: Result Reporting & Integration**
    *   **Goal:** Send processed job listings back up the hierarchy via MCP.
    *   **Tasks:** Format filtered job listings into the standard MCP message structure, report results to the (conceptual) Job Search Manager.
    *   **Success Criteria:** Filtered, structured job data is successfully transmitted via MCP.

*   **Future Phases (Longer-Term):**
    *   Implement the Job Search Manager agent.
    *   Develop Profile Management agents (Resume, LinkedIn profile parsing).
    *   Implement advanced Job Evaluation agent using semantic matching (AI APIs).
    *   Develop Application Processing agents (document customization, form filling).
    *   Integrate other job sources (Indeed, company career pages).
    *   Implement Coordinator Agent logic.
    *   Develop frontend/UI for user interaction and monitoring.
    *   Enhance data storage (e.g., SQLite).

## 7. Technology Stack (Current & Planned)

*   **Core Environment:** Python 3.11 (Conda env on macOS)
*   **Agent Framework:** Custom implementation using `AgtBase` and MCP. (Potential future integration with LangChain/CrewAI).
*   **Communication:** Custom Message Control Protocol (MCP) implementation.
*   **Web Automation:** Playwright (for LinkedIn interaction).
*   **Data Storage:** JSON (for credentials, preferences, initial job data). (Planned migration to SQLite/DuckDB).
*   **Scheduling:** (Planned) APScheduler or Celery for background operation.
*   **AI/ML:** (Planned) Sentence-Transformers for local embeddings, GPT/Claude APIs for advanced semantic understanding and generation tasks.
*   **Frontend:** (Planned) Streamlit for visualization and user interaction.

This plan provides a clear path forward, focusing on delivering the core LinkedIn job search functionality incrementally while keeping the broader architectural vision in mind.
