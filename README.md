\# llm-quiz-solver



FastAPI app that accepts quiz tasks (POST), solves data tasks in a headless-browser+python worker,

and submits answers. Built for the course quiz evaluation.



\## Run locally



1\. Create a venv and install deps:

&nbsp;  python -m venv venv

&nbsp;  .\\venv\\Scripts\\Activate.ps1

&nbsp;  python -m pip install -r requirements.txt



2\. Set environment variables (or create .env):

&nbsp;  STUDENT\_EMAIL=you@example.com

&nbsp;  STUDENT\_SECRET=<your\_secret>

&nbsp;  BASE\_SYSTEM\_PROMPT="..."

&nbsp;  BASE\_USER\_PROMPT="..."



3\. Run:

&nbsp;  python -m uvicorn app.main:app --reload --port 8000



\## Deploy

This repo is designed to be deployed on Railway/Render. Provide the env variables in the platform's UI.



\## License

MIT



