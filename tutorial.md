# CrowdSim AI - Tutorial

Welcome to **CrowdSim AI**, an enterprise-grade social simulation platform where AI agents with distinct personas interact, use tools, and provide feedback on products and ideas.

## Architecture Overview

CrowdSim AI has evolved into a robust system featuring Agent2Agent protocols, Observability, and Containerization.

```mermaid
graph TD
    User[User] -->|Interacts with| UI[Web UI (app.py)]
    UI -->|Calls| SimScript[Simulation Logic (simulation.py)]
    
    subgraph "Enterprise Layer"
        SimScript -->|Logs/Traces| Observability[Observability (Structured Logs)]
        SimScript -->|Evaluates| Evaluator[LLM-as-a-Judge]
        SimScript -->|Persists| SessionMgr[Session Manager]
    end
    
    subgraph "TinyTroupe Environment"
        SimScript -->|Initializes| World[TinyWorld]
        World -->|Contains| Agents[TinyPerson Agents]
        Agents -->|A2A Protocol| Agents
    end
    
    subgraph "External Capabilities"
        Agents -->|Call| WebSearch[Web Search Tool]
        SimScript -->|Calls| Sentiment[Sentiment Analysis Tool]
    end
    
    SessionMgr -->|Saves to| Disk[JSON Sessions]
    Evaluator -->|Scores| QualityMetrics[Relevance/Coherence/Fidelity]
    SimScript -->|Returns Results| UI
```

## 1. Features

### 🧠 Intelligent Agents
- **ReAct Pattern**: Agents can reason and use tools.
- **Web Search**: Agents can look up real-time information via DuckDuckGo.
- **Context Awareness**: Agents maintain state across turns.

### 💾 Context Engineering
- **Sessions**: Pause and resume simulations using Session IDs.
- **Long-term Memory**: Agent memories are persisted to disk.

### 📊 Observability & Quality
- **Structured Logs**: JSON logs with Trace IDs for debugging.
- **Quality Assurance**: Automated "LLM-as-a-Judge" scores every response for Relevance, Coherence, and Persona Fidelity.

### 🚀 Enterprise Readiness
- **Dockerized**: Fully containerized for easy deployment.
- **A2A Protocol**: Standardized message schema for robust communication.

## 2. Installation & Setup

### Option A: Docker (Recommended)
Run the entire stack with a single command.

1.  **Create `.env` file**:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```
2.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```
3.  **Access the UI**: Open `http://localhost:8501`.

### Option B: Local Python Setup

1.  **Create Virtual Environment**:
    ```bash
    python -m venv .venv
    # Activate: .venv\Scripts\activate (Windows) or source .venv/bin/activate (Mac/Linux)
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## 3. Usage Guide

### Running a Simulation
1.  Open the Web UI.
2.  **Configure**: Enter your product pitch or question.
3.  **Context**: Add any background information.
4.  **Run**: Click "Run Simulation".

### Resuming a Session
To resume a previous conversation (CLI only for now):
```bash
python simulation.py --session_id <YOUR_SESSION_ID>
```

## 4. Understanding Results

### Dashboard Metrics
- **Sentiment Score**: (0-10) How positive the agents feel.
- **Quality Scores**: (0-5)
    - **Relevance**: Did they answer the question?
    - **Coherence**: Does it make sense?
    - **Fidelity**: Does it match their persona?

### Logs
- **Simulation Logs**: Check `logs/simulation.jsonl` for detailed, machine-readable logs.
- **Conversation Logs**: View the full transcript in the UI or the generated PDF report.
