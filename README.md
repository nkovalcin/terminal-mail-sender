# Terminal Mail Sender

A Python CLI tool for sending personalized bulk emails from your terminal. Supports CSV company lists, customizable templates, test mode, and rate limiting.

## Features

- **CSV-based contact list** — load companies from CSV with name, industry, email, location
- **Template system** — use `{{placeholders}}` for personalized emails
- **Test mode** — preview what would be sent without actually sending
- **Rate limiting** — configurable delay between emails
- **Progress tracking** — real-time progress and summary statistics
- **Error handling** — graceful handling of failed sends

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/nkovalcin/terminal-mail-sender.git
cd terminal-mail-sender

# 2. Set up config
cp config.example.json config.json
# Edit config.json with your SMTP credentials

# 3. Prepare your contacts
cp companies.example.csv companies.csv
# Add your contacts to companies.csv

# 4. Test first
python3 mail_sender.py --test

# 5. Send
python3 mail_sender.py
```

## Usage

```bash
# Test mode (recommended first)
python3 mail_sender.py --test

# Send with default settings
python3 mail_sender.py

# Send first 10 emails with 2s delay
python3 mail_sender.py --max 10 --delay 2

# Use custom files
python3 mail_sender.py --csv my_contacts.csv --template my_template.txt
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--csv` | `companies.csv` | CSV file with contacts |
| `--template` | `email_template.txt` | Email template file |
| `--config` | `config.json` | SMTP configuration |
| `--delay` | `1.0` | Seconds between emails |
| `--test` | — | Preview without sending |
| `--max` | all | Maximum emails to send |

## Template Variables

| Variable | Description |
|----------|-------------|
| `{{Company Name}}` | Company name from CSV |
| `{{Industry}}` | Industry/sector |
| `{{Email}}` | Email address |
| `{{Location}}` | Geographic location |

## Gmail Setup

1. Enable 2-factor authentication
2. Generate an app password: https://myaccount.google.com/apppasswords
3. Use the app password in `config.json`

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT
