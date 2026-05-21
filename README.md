# notion-daily-quote-automation

Fetches a random quote by category from [API Ninjas](https://api-ninjas.com/api/quotes) and inserts it into a Notion database daily via GitHub Actions.

## Notion setup

### 1. Create the database

1. In Notion, create a new page and type `/database` → select **Table - Full page**
2. Add the following properties (the **Quote** title column already exists by default):

   | Property   | Type         |
   | ---------- | ------------ |
   | Quote      | Title        |
   | Author     | Rich text    |
   | Date       | Date         |
   | Category   | Multi-select |
   | Work       | Rich text    |
   | Source     | URL          |
   | Created By | Select       |

3. Copy the **database ID** from the URL:
   ```
   https://www.notion.so/<workspace>/<DATABASE_ID>?v=...
   ```
   The DATABASE_ID is the 32-character string before `?v=`. This is your `NOTION_QUOTES_DB_ID`.

### 2. Create a Notion integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) and click **New integration**
2. Give it a name (e.g. `daily-quotes-connection`) and select your workspace
3. Click **Save** → copy the **Internal Integration Token** — this is your `NOTION_TOKEN`

### 3. Connect the integration to your database

1. Open your quotes database in Notion
2. Click **`...`** (top-right) → **Connections** → **Connect to** → select your integration
3. If the database is embedded inside another page, open that **parent page** and connect the integration there instead

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
