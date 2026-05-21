# notion-daily-quote-automation

Fetches a random quote by category from [API Ninjas](https://api-ninjas.com/api/quotes) and inserts it into a Notion database daily via GitHub Actions. Optionally displays today's quote on any Notion page in a styled quote block.

## Prerequisites

- Python 3.11+
- A [Notion](https://notion.so) account
- An [API Ninjas](https://api-ninjas.com) account (free tier works)

---

## Notion setup

### 1. Create the quotes database

1. In Notion, create a new page and type `/database` → select **Table - Full page**
2. Add the following properties (**Quote** title column exists by default):

   | Property   | Type         |
   | ---------- | ------------ |
   | Quote      | Title        |
   | Author     | Rich text    |
   | Date       | Date         |
   | Category   | Multi-select |
   | Work       | Rich text    |
   | Source     | URL          |
   | Created By | Select       |

3. Copy the **database ID** from the URL — it's the 32-character string before `?v=`:
   ```
   https://www.notion.so/<DATABASE_ID>?v=...
   ```

### 2. Create a Notion integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → **New integration**
2. Name it (e.g. `daily-quotes-connection`), select your workspace, and click **Save**
3. Copy the **Internal Integration Token** — this is your `NOTION_TOKEN`

### 3. Connect the integration

Connect the integration to every Notion page it needs to access:

- **Quotes database** — open the database → **`...`** → **Connections** → **Connect to** → select your integration
- **Quote display page** *(optional)* — if you want today's quote shown on a separate page, connect the integration to that page the same way

> If your database or page is embedded inside another page, connect the integration to the **parent page** instead.

---

## Local setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

3. Run the script:

   **Windows (PowerShell)**
   ```powershell
   Get-Content .env | ForEach-Object {
       if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
           [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
       }
   }
   python daily_quote.py
   ```

   **Linux / macOS**
   ```bash
   export $(grep -v '^#' .env | xargs)
   python daily_quote.py
   ```

---

## GitHub Actions setup

Add these secrets to your repository under **Settings → Secrets and variables → Actions**:

| Secret                  | Required | Description                                          |
| ----------------------- | -------- | ---------------------------------------------------- |
| `NOTION_TOKEN`          | Yes      | Notion integration token                             |
| `NOTION_QUOTES_DB_ID`   | Yes      | Notion quotes database ID                            |
| `API_NINJAS_KEY`        | Yes      | API Ninjas API key                                   |
| `QUOTE_CATEGORY`        | No       | Quote category, e.g. `wisdom` (default: `wisdom`)    |
| `NOTION_QUOTE_PAGE_ID`  | No       | Page ID to display today's quote as a styled block   |
| `TIMEZONE`              | No       | Timezone for the date (default: `America/New_York`)  |

The workflow runs daily at **12:17 UTC** and can also be triggered manually via **workflow_dispatch**.

---

## How it works

1. Fetches a random quote from API Ninjas for the configured category
2. Creates a new row in the Notion quotes database with the quote, author, date, and category
3. If `NOTION_QUOTE_PAGE_ID` is set, replaces the content of that page with today's quote in a styled block:

   > **Quote text**
   > — Author
