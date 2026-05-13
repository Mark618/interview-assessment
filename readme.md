Technical Assessment

An automated, AI-driven word game engine built with n8n, Google Gemini, and Google Sheets.
Setup & Installation

This project is designed to run in a self-hosted environment using Docker.
## 1. Prerequisites
- Docker installed on your machine.  
- A Google Cloud Project with Google Sheets API and Google Drive API enabled.  
- A Google Gemini API Key (obtained via Google AI Studio).

## 2. Running n8n with Docker

Run the following command to start the n8n container.  
Note: We are using the standard n8n image. All custom logic is handled via JavaScript Code Nodes to ensure compatibility without a separate Python runtime.

```Bash
docker volume create n8n_data

docker run -it \
  --name n8n-wordchain \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```
## 3. Importing the Workflow

Open your browser and go to http://localhost:5678.

Follow the initial setup prompts to create an account or login to existing account.

In the n8n canvas, click on the Workflow Menu (three dots) -> Import from File.

Select the workflow.json file included.

## 4. Configuring Credentials

To make the workflow functional, you must add your own credentials:

Google Gemini API: Use your Gemini API key.

Google Sheets API: Authenticate via OAuth2 or Service Account to access the game database.

## 5. How to Play

Open the Chat UI by clicking the "Chat" button at the bottom left of the n8n canvas.

Start a Game: Type start easy, start medium, or start hard.

Play a Word: Type submit [your_word].

    Example: submit apple

Check Stats: Type stats to see your leaderboard standing and career performance.