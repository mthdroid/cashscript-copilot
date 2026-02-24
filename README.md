# CashScript Copilot

**AI-Powered Smart Contract Development Assistant for Bitcoin Cash**

CashScript Copilot is an intelligent development tool that helps developers write, audit, explain, and optimize CashScript smart contracts on Bitcoin Cash. It leverages large language models with deep CashScript domain knowledge to accelerate BCH smart contract development.

## Features

### Generate
Describe what you want in natural language, get complete, compilable CashScript code.
- Supports all CashScript features: covenants, CashTokens (fungible + NFT), time locks, multi-sig
- Follows security best practices automatically
- Includes inline comments and usage notes

### Audit
Paste any CashScript contract and get a comprehensive security analysis.
- Severity-rated findings (CRITICAL / HIGH / MEDIUM / LOW / INFO)
- Checks for: missing output validation, token confusion, signature issues, value drain, replay attacks
- Provides fixed code with all issues resolved
- Overall security rating (A-F)

### Explain
Get plain-language explanations of any CashScript contract.
- Function-by-function breakdown
- Token flow analysis
- Security model description
- ASCII flow diagrams

### Optimize
Submit a contract for improvement suggestions.
- Security hardening
- Efficiency improvements
- Code quality and readability
- Complete rewritten optimized version

### Chat
Free-form conversation about CashScript development, Bitcoin Cash, CashTokens, covenants, and more.
- Conversation history persisted in browser (localStorage)
- Context-aware follow-up questions

### Extra Features
- **Dark/Light theme toggle** - Switch between dark and light mode (preference saved)
- **JSON Export** - Export audit and optimization reports as structured JSON
- **Code download** - Download generated contracts as `.cash` files
- **Keyboard shortcuts** - Ctrl+Enter to submit in any mode

## Quick Start

```bash
# Clone
git clone https://github.com/mthdroid/cashscript-copilot.git
cd cashscript-copilot

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY

# Run
python app.py
# Open http://localhost:5050
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `anthropic` | AI provider: `anthropic` or `openai` |
| `ANTHROPIC_API_KEY` | - | Anthropic Claude API key |
| `OPENAI_API_KEY` | - | OpenAI API key (if using openai provider) |
| `AI_MODEL` | auto | Override default model |
| `SECRET_KEY` | dev key | Flask secret key |

## Deployment

### Railway (recommended)

1. Push your repo to GitHub
2. Go to [Railway.app](https://railway.app), create a new project from GitHub repo
3. Add environment variables: `ANTHROPIC_API_KEY`, `AI_PROVIDER=anthropic`
4. Railway auto-detects `railway.json` and deploys

### Render

1. Go to [Render.com](https://render.com), create a new Web Service from GitHub repo
2. Render auto-detects `render.yaml` config
3. Add your `ANTHROPIC_API_KEY` in the dashboard

### Manual (VPS/local)

```bash
pip install -r requirements.txt
python app.py --production --host 0.0.0.0 --port 8080
```

## Architecture

```
cashscript-copilot/
├── app.py                    # Flask web server + API routes
├── ai_engine.py              # LLM integration (Anthropic/OpenAI)
├── cashscript_knowledge.py   # CashScript reference + examples + audit checklist
├── templates/
│   └── index.html            # Web UI (Tailwind CSS, highlight.js, marked.js)
├── examples/                 # Example CashScript contracts
│   ├── escrow.cash
│   ├── token_sale.cash
│   └── token_vesting.cash
├── Procfile                  # For Railway/Render/Heroku deployment
├── railway.json              # Railway deployment config
├── render.yaml               # Render deployment config
├── requirements.txt
├── .env.example
└── README.md
```

## CashScript Knowledge Base

The AI engine includes comprehensive CashScript knowledge:

- **Complete language reference**: Types, functions, introspection opcodes, CashTokens
- **5 built-in example contracts**: Escrow, Token Sale, DAO Voting, Token Vesting, NFT Marketplace
- **Security audit checklist**: 15+ vulnerability checks across 4 severity levels
- **Common patterns**: Time locks, covenants, multi-sig, rate limiting, token vaults
- **Best practices**: Output validation, token category verification, dust limits, replay protection

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/generate` | POST | Generate contract from description |
| `/api/audit` | POST | Security audit of contract code |
| `/api/explain` | POST | Explain contract in plain language |
| `/api/optimize` | POST | Optimize contract code |
| `/api/chat` | POST | Free-form CashScript Q&A |
| `/api/example/<name>` | GET | Get example contract code |
| `/api/health` | GET | Health check |

## Tech Stack

- **Backend**: Python + Flask
- **AI**: Anthropic Claude / OpenAI GPT (configurable)
- **Frontend**: Tailwind CSS, highlight.js (syntax highlighting), marked.js (Markdown rendering)
- **Domain Knowledge**: Custom CashScript language reference, patterns, and security checklist

## BCH-1 Hackcelerator

This project was built for the **BCH-1 Hackcelerator** hackathon on DoraHacks.

- **Track**: Technology (Developer Tooling)
- **Prize Pool**: $40,000 USD
- **Ecosystem**: Bitcoin Cash

## License

MIT
