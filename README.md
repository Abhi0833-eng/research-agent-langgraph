# Autonomous Research and Report Agent

A LangGraph-based research pipeline that searches the web, verifies claims with an LLM, writes a report, and reviews the draft before returning the final result.

## Pipeline

```text
Research -> Fact-check -> Write -> Critique
                         ^          |
                         |----------|
                         revise until approved or max iterations reached
```

## Requirements

- Python 3.10 or newer
- A Tavily API key
- A Groq API key
- Git, if cloning the repository

## Setup

Clone the repository and enter its folder:

```powershell
git clone https://github.com/Abhi0833-eng/research-agent-langgraph.git
cd research-agent-langgraph
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a file named `.env` in the project root:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
LANGSMITH_TRACING=false
```

Never commit `.env` or share its API keys.

## Run

Start the interactive application:

```powershell
python main.py
```

Enter a research question when prompted. The application searches for sources, extracts verified facts, drafts a report, and runs a critic review.

## Web Interface

Start the browser-based API and interface with Uvicorn:

```powershell
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` in a browser and submit a research question. The interface calls `POST /research` and displays the report, verified facts, flagged issues, and sources. A simple health check is available at `GET /health`.

## Deploy on Render

The repository includes `render.yaml` for deployment on Render:

1. Sign in at [render.com](https://render.com) and choose **New > Blueprint**.
2. Connect `Abhi0833-eng/research-agent-langgraph`.
3. Select the `render.yaml` file and create the web service.
4. In the service environment settings, add `TAVILY_API_KEY` and `GROQ_API_KEY` using your own keys. Keep them secret.
5. Wait for the deployment to finish, then open the generated `onrender.com` URL.

Render runs the service with `uvicorn app:app --host 0.0.0.0 --port $PORT` and checks `GET /health`.

## Free Alternative: Hugging Face Spaces

If Render asks for payment verification, create a Docker Space at [huggingface.co/new-space](https://huggingface.co/new-space):

1. Choose an owner, enter a Space name, select **Docker**, and choose the free CPU hardware.
2. Clone the new Space repository locally or upload the project files from this repository.
3. In the Space **Settings**, add these secrets:
    `TAVILY_API_KEY`, `GROQ_API_KEY`, and `LANGSMITH_TRACING=false`.
4. Wait for the build to finish and open the Space URL.

The included `Dockerfile` starts the FastAPI interface on Hugging Face's port `7860`. Free Spaces can sleep after inactivity, so the first request after a pause may take longer.

## Free Hosting: Streamlit Community Cloud

Streamlit Community Cloud can host the browser interface directly from this GitHub repository:

1. Open [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Create app** and select this repository and the `main` branch.
3. Set the main file path to `streamlit_app.py`.
4. Open **Advanced settings** and add these secrets:

```toml
TAVILY_API_KEY = "your_tavily_api_key"
GROQ_API_KEY = "your_groq_api_key"
LANGSMITH_TRACING = "false"
```

5. Click **Deploy**. Streamlit will provide a public URL for users.

The free tier may sleep when unused, and the first request after sleeping can take longer. API keys must be added as secrets, never committed to GitHub.

## Test

Run the standalone pipeline test:

```powershell
python test_research.py
```

## Project Structure

```text
research-agent-langgraph/
|-- agents/
|   |-- research_agent.py
|   |-- fact_checker_agent.py
|   |-- writer_agent.py
|   `-- critic_agent.py
|-- state/
|   `-- schema.py
|-- static/
|   `-- index.html
|-- app.py
|-- render.yaml
|-- streamlit_app.py
|-- main.py
|-- test_research.py
|-- requirements.txt
`-- .env                 local secrets, not committed
```

## Shared State

`state/schema.py` defines the `ResearchState` TypedDict shared by every graph node. It stores the query, sources, verified facts, flagged issues, draft history, critique feedback, approval status, and iteration limits.

## LangSmith Tracing

LangSmith tracing is optional. Keep it disabled with:

```env
LANGSMITH_TRACING=false
```

To enable tracing, configure a valid `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT` for the correct LangSmith workspace, then set `LANGSMITH_TRACING=true`.
