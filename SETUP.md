# LaunchMind Setup Guide

Complete these steps in order. **Total time: ~30 minutes**

## ✅ Step 1: Create GitHub Repository (5 min)

1. Go to https://github.com/new
2. Repository name: `launchmind-fizan`
3. Make it **PUBLIC** (required for evaluator to see)
4. Click "Create repository"

## ✅ Step 2: Create GitHub Token (5 min)

1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Click "Generate new token"
3. Name it: `LaunchMind`
4. Set Expiration: 30 days (or longer)
5. Scopes:
   - ✅ repo (full control)
   - ✅ workflow
6. Click "Generate token"
7. **Copy the token immediately** - you won't see it again
8. Save it somewhere safe temporarily

## ✅ Step 3: Create Slack Workspace & Bot (10 min)

### Create workspace (if needed):
1. Go to slack.com
2. Sign up for free workspace
3. Name it anything (e.g., "LaunchMind Demo")

### Create bot:
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: `LaunchMind Bot`
5. Pick your workspace
6. Go to "OAuth & Permissions" (left sidebar)
7. Under "Bot Token Scopes", add:
   - `chat:write`
   - `channels:read`
   - `channels:join`
8. Click "Install to Workspace"
9. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### Create #launches channel:
1. In your Slack workspace, click "+" next to "Channels"
2. Create channel: `#launches`
3. In #launches, type: `/invite @LaunchMindBot`
4. Bot is now in the channel

## ✅ Step 4: Set Up SendGrid (10 min)

1. Go to sendgrid.com
2. Click "Free" → Sign up
3. Verify email (check inbox, click link)
4. In SendGrid dashboard, go to Settings → API Keys
5. Click "Create API Key"
6. Name it: `LaunchMind`
7. Permissions: Check "Mail Send"
8. Click "Create & Copy"
9. **Copy the API key** (starts with `SG.`)

### Verify sender:
1. Go to Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Email: `muhammadfaiza9876@gmail.com`
4. Fill in First Name: `Auto`
5. Last Name: `Test`
6. Click "Create"
7. **Check your email** - click verification link

## ✅ Step 5: Get Anthropic API Key (2 min)

1. Go to console.anthropic.com
2. Sign in or create account
3. Go to API keys section
4. Create a new API key
5. Copy it (starts with `sk-ant-`)

## ✅ Step 6: Create .env File (3 min)

In the `launchmind` directory, create a file named `.env` with:

```
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_REPO=justfordeployment123/launchmind-fizan
SLACK_BOT_TOKEN=xoxb-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SENDGRID_API_KEY=SG.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SENDGRID_FROM_EMAIL=muhammadfaiza9876@gmail.com
SENDGRID_TO_EMAIL=muhammadfaiza9876@gmail.com
```

Replace the X's with your actual tokens/keys from steps 2-5.

## ✅ Step 7: Install Python Dependencies (3 min)

```bash
cd /Users/muhammadfizantariq/Documents/agentic/launchmind

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import anthropic, requests, slack_sdk, sendgrid; print('✅ All imports OK')"
```

## ✅ Step 8: Test Each Integration (5 min)

### Test GitHub:
```bash
export GITHUB_TOKEN="your_token_here"
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
# Should return your GitHub user data
```

### Test Slack:
```bash
python -c "from slack_sdk import WebClient; print('✅ Slack SDK works')"
```

### Test SendGrid:
```bash
python -c "from sendgrid import SendGridAPIClient; print('✅ SendGrid SDK works')"
```

### Test Anthropic:
```bash
python -c "from anthropic import Anthropic; print('✅ Anthropic SDK works')"
```

## ✅ Step 9: Run the System

```bash
cd /Users/muhammadfizantariq/Documents/agentic/launchmind
python main.py
```

The system will:
1. Print CEO receiving startup idea
2. Send tasks to Product, Engineer, Marketing agents
3. Generate product spec
4. Create GitHub issue and PR
5. Send email to your inbox
6. Post message to Slack #launches
7. Run QA review
8. Print complete message history

## ✅ Step 10: Verify Everything Worked

Check each platform:

- **GitHub**: Go to justfordeployment123/launchmind-fizan → Pull requests
  - Should see 1 PR titled "Initial landing page"
  
- **Slack**: Open #launches channel
  - Should see a message from LaunchMind Bot with the launch details
  
- **Email**: Check muhammadfaiza9876@gmail.com
  - Should see email from your SendGrid verified address
  
- **Terminal**: Look for "MESSAGE HISTORY" section
  - Should show all JSON messages between agents

## ⚠️ Common Mistakes

❌ **Tokens in code**: Never hardcode API keys  
✅ Use `.env` file + `os.environ.get()`

❌ **Slack bot not in channel**: Bot must be invited to #launches  
✅ Type `/invite @LaunchMindBot` in the channel

❌ **SendGrid email bounces**: From email must be verified  
✅ Verify the sender in SendGrid settings

❌ **GitHub PR not showing**: Token may lack permissions  
✅ Regenerate token with `repo` + `workflow` scopes

## 🎬 Recording Demo Video

Once everything works:

1. Open terminal in the launchmind directory
2. Make terminal window large and visible
3. Run: `python main.py`
4. Record entire output (8-10 minutes)
5. While recording, show:
   - Terminal output with agent messages
   - GitHub repo page (refresh to show PR)
   - Slack #launches channel
   - Email inbox
   - Terminal message history at end
6. Save video as MP4
7. Upload to YouTube or Google Drive (get public link)

## ✅ Checklist Before Submitting

- [ ] `.env` file created with all 7 environment variables
- [ ] `.env` is in `.gitignore` (no secrets in repo)
- [ ] GitHub repo is PUBLIC
- [ ] Slack bot is in #launches channel
- [ ] SendGrid verified sender email set
- [ ] `python main.py` runs without errors
- [ ] GitHub PR is visible in repo
- [ ] Slack message appears in #launches
- [ ] Email arrives in inbox
- [ ] Demo video recorded (8-10 min)
- [ ] Demo video shows feedback loop (CEO revision request)
- [ ] Message history printed at end

## 🆘 Stuck?

1. Check `.env` file has all 7 variables
2. Run `python main.py` and look for first error message
3. Search the error in README.md "Troubleshooting" section
4. Ensure no typos in tokens (copy-paste carefully)
5. Verify token permissions (GitHub token needs `repo` scope)

---

**Next Step**: Run `python main.py` after setup is complete!
