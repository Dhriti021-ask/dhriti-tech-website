## Python Customer Support Chatbot

This repository now includes a Python chatbot (`chatbot.py`) that can help banks (or any industry) manage customer support.

### Features
- Banking support flows (fraud, card issues, loans, password reset)
- Generic industry support mode
- Intent detection using configurable keyword rules
- Automatic escalation and ticket creation (`TKT-...`)
- Ticket export to `tickets.json`

### Run
```bash
python chatbot.py
```

Then choose:
- `banking` for bank-focused support behavior
- `general` for non-banking industries

Type `exit` to quit.

### Customize
Inside `chatbot.py` you can modify:
- `self.intents` to add new intent keywords
- `self.faq` to add FAQ answers
- `_handle_banking` and `_handle_generic_industry` for business-specific logic
