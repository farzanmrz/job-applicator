# Autonomous Job Applicator Agent

This repository contains the developmental journey and final implementation of an autonomous agent designed to streamline the professional recruitment cycle.

The project's initial vision was to create a full-stack agentic solution for job discovery, profile management, and automated application submission. **Due to the complexities discovered during development, the project's scope was strategically focused on perfecting the most critical foundational module: the AI-Powered Profile Manager.**

This README outlines the original vision and provides a deep dive into the implemented profile consolidation engine, detailing the extensive exploration of various AI frameworks that led to the final architecture.

## Implemented Core Module: The AI-Powered Profile Manager

The final, implemented artifact is a powerful and robust version of the Profile Manager. This module successfully automates the extraction, comparison, and consolidation of professional data using a sophisticated agentic workflow.

* **Architecture**: The system uses a Directed Acyclic Graph (DAG) of specialized AI agents, orchestrated by the **Microsoft AutoGen** framework. This allows for a clear, maintainable, and robust flow of information between agents.
* **AI & Processing**: The entire pipeline runs offline on consumer-grade hardware, leveraging the power of local Small Language Models (SLMs) like **Qwen and DeepSeek** deployed via **Ollama**.
* **Reliability**: The system achieves high-fidelity output through meticulous prompt engineering with **few-shot examples** and enforces a strict JSON schema for all agent outputs using **Pydantic models**.

## Technical Deep Dive & Framework Exploration

The journey to this final architecture involved rigorous, hands-on evaluation of the modern agentic AI landscape. The initial, ambitious goal of an end-to-end job applicator required tools for web interaction and complex agent coordination, leading to the exploration of several frameworks.

### Frameworks Explored & Lessons Learned

The final choice of **Microsoft AutoGen** was the result of a deliberate process of elimination, providing deep insights into the practical trade-offs of each tool.

* **Playwright & Web Automation**: Early prototypes used Playwright for live web scraping. This was **abandoned due to the inherent brittleness** of browser automation, frequent UI changes on target sites, and the complexity of managing authentication state. The project pivoted to offline PDF processing for enhanced reliability.

* **LangChain & LangGraph**: These were explored for their "Message Control Protocol" (MCP) concept and agentic building blocks. However, for this project's multi-agent, structured data task, the frameworks were found to add **significant complexity and abstraction overhead** without providing enough control over the agent interaction logic.

* **CrewAI & Smol-agents**: As the search continued for a more suitable framework, both CrewAI (with its role-based design) and the lightweight Smol-agents were evaluated. While both are powerful, **AutoGen was ultimately selected** for its superior flexibility in defining complex, multi-agent conversations via a Directed Acyclic Graph (DiGraph), which was a perfect fit for the project's data pipeline structure.

* **Microsoft AutoGen (Final Choice)**: AutoGen provided the ideal balance of power and control. Its graph-based orchestration allowed for a declarative, maintainable, and highly effective way to manage the flow of data between specialized LLM agents, proving to be the most robust solution for the task.

This iterative development process, documented in the issues and `docs/` folder, turned the project into a comprehensive case study on selecting the right tools for building modern AI systems.

## License

This project is licensed under the [MIT License](LICENSE).
