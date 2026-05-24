# Confluence Automation

Create, update, and search Confluence pages from natural language via Claude Code. Works with Atlassian Cloud and Server/DC.

> If this saves you time, a ⭐ on the repo helps others find it.

## Install

```bash
git clone https://github.com/dev-vpandey/ai-confluence-automation.git
cd ai-confluence-automation
./install.sh
```

Prompts for your Confluence URL, default space, and PAT token. Sets up venv, config, and Claude Code skill automatically.

**Requirements:** Python 3.9+, Claude Code CLI

## Usage

Open Claude Code and describe what you want:

```
Create an architecture page in ENG space for our new data pipeline
```

```
Search Confluence for "authentication" in ENG space
```

The skill picks the right template, creates the page, and returns the URL.

**Direct CLI** (without Claude Code):

```bash
source venv/bin/activate
python src/confluence_page.py create SPACE "Title" content.html
python src/confluence_page.py update PAGE_ID "Title" content.html
python src/confluence_page.py search "keyword" SPACE
```

## Authentication

Set `CONFLUENCE_TOKEN` in your shell profile (done by `install.sh`). PAT is the recommended auth method for all users.

Cookie fallback available for Server/DC only — run `./refresh-auth --guided` to set up.

> Atlassian Cloud: PAT only. Cookie auth is not supported.

## Docs

- [User Guide](documentation/USER-GUIDE.md) — full usage, templates, troubleshooting
- [Design Doc](documentation/architecture/DESIGN-DOC.md) — architecture and decisions
- [Changelog](CHANGELOG.md) — what changed per version
