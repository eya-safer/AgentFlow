<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/92ba1c39-21a8-4320-992e-736efe43ac0e" />

# AgentFlow — AI-Powered Business Assistant

AgentFlow is an intelligent business assistant powered by AI agents and Google's Gemini API. It enables users to interact with business data through natural language, retrieve customer and order information, and prepare customer notifications with a human approval workflow.

The project combines **LLM Function Calling, tool execution, conversational memory, and Human-in-the-Loop (HITL)** in a full-stack application.

## Key Features

- **AI Agent & Function Calling:** Uses Gemini to understand user requests and select the appropriate business tools.
- **Customer Management:** Retrieve customer information from a database.
- **Order Tracking:** Check order status and retrieve customer orders.
- **Human-in-the-Loop:** Prepare customer notifications and require human approval or rejection before considering them authorized.
- **Conversational Memory:** Store conversations and messages in SQLite and resume previous discussions.
- **Approval Center:** Review pending notifications and manage approval decisions.
- **Chat Interface:** Interact with the AI agent through a React-based interface.
- **Conversation History:** Browse and continue previous conversations.

## Architecture

```text
                User
                  |
                  v
          React + TypeScript
             Frontend
                  |
               FastAPI
                  |
                  v
           Business AI Agent
                  |
             Gemini API
          (Function Calling)
                  |
          +-------+--------+
          |       |        |
          v       v        v
       Customer  Orders  Notifications
         Tools    Tools     Tool
          |       |        |
          +-------+--------+
                  |
               SQLite
                  |
          Human Approval
          (Approve / Reject)
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| AI | Google Gemini API, Function Calling |
| Database | SQLite, SQLAlchemy |
| Validation | Pydantic |
| Testing | Pytest |
| HTTP Client | Axios |

## Project Structure

```text
AgentFlow/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── services/
│   │   └── tools/
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       └── types/
│
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js and npm
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/eya-safer/AgentFlow.git
cd AgentFlow
```

### 2. Configure the backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a `.env` file at the project root using `.env.example` as a template, then add your Gemini API key.

### 3. Run the backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

### 4. Run the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

## Testing

Run backend tests from the project root:

```bash
python -m pytest backend/tests -v
```

Build the frontend for production:

```bash
cd frontend
npm run build
```

## Key Concepts

- **AI Agents:** Autonomous selection and execution of business tools based on user intent.
- **Function Calling:** Structured interaction between Gemini and Python functions.
- **Human-in-the-Loop:** Human validation before sensitive business actions are authorized.
- **Conversational Memory:** Persistent storage and retrieval of conversation context.

## Future Improvements

- Authentication and role-based access control.
- More business tools and integrations.
- Advanced agent monitoring and execution tracing.
- Real notification delivery after explicit authorization.
- Deployment and production configuration.

## Author

**Eya Safer**

Software Engineering Student | Full-Stack Development & Artificial Intelligence

[GitHub](https://github.com/eya-safer)
