# notion-daily-quote-automation

Fetches a random quote by category from [API Ninjas](https://api-ninjas.com/api/quotes) and inserts (or updates) it in a Notion database daily via GitHub Actions.

## Notion database schema

| Property   | Type         |
| ---------- | ------------ |
| Quote      | Title        |
| Author     | Rich text    |
| Date       | Date         |
| Category   | Multi-select |
| Work       | Rich text    |
| Source     | URL          |
| Created By | Select       |

## Local setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```

3. Run the script (PowerShell / Windows):
   ```powershell
   Get-Content .env | ForEach-Object {
       if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
           [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
       }
   }
   python daily_quote.py
   ```

   Or on Linux/macOS:
   ```bash
   export $(grep -v '^#' .env | xargs)
   python daily_quote.py
   ```

## GitHub Actions secrets

Add these secrets to your repository (Settings → Secrets and variables → Actions):

| Secret                | Description                              |
| --------------------- | ---------------------------------------- |
| `NOTION_TOKEN`        | Notion integration token                 |
| `NOTION_QUOTES_DB_ID` | Notion database ID                       |
| `API_NINJAS_KEY`      | API Ninjas API key                       |
| `QUOTE_CATEGORY`      | Quote category (e.g. `wisdom`, optional) |

The workflow runs daily at 12:17 UTC and can also be triggered manually via **workflow_dispatch**.
