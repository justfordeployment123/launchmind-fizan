# 🔑 API Keys - Direct Links & Instructions

## ✅ 1. OpenAI API Key (You Already Have This!)

**Link**: https://platform.openai.com/account/api-keys

**Instructions**:
1. Go to https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-`)
4. Save in .env as: `OPENAI_API_KEY=sk-proj-xxxxx`

**Note**: You said you already have this, so just copy it and paste in .env file!

---

## 2. GitHub Personal Access Token

**Link**: https://github.com/settings/tokens

**Step-by-Step**:
1. Go to https://github.com/settings/tokens
2. Click "Tokens (classic)" in left sidebar
3. Click "Generate new token"
4. Name: `LaunchMind`
5. Expiration: 30 days (or longer)
6. **Check these scopes**:
   - ✅ `repo` (full control of repositories)
   - ✅ `workflow` (update GitHub action workflows)
7. Click "Generate token"
8. **COPY IMMEDIATELY** (you won't see it again!)
9. Save in .env as: `GITHUB_TOKEN=ghp_xxxxx`

---

## 3. Slack Bot Token

**Link**: https://api.slack.com/apps

**Step-by-Step**:
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. App name: `LaunchMind Bot`
5. Select your workspace
6. Go to "OAuth & Permissions" (left menu)
7. Scroll to "Bot Token Scopes"
8. Click "Add an OAuth Scope"
9. **Add these scopes**:
   - ✅ `chat:write` (post messages)
   - ✅ `channels:read` (read channel list)
   - ✅ `channels:join` (join channels)
10. Click "Install to Workspace"
11. Copy "Bot User OAuth Token" (starts with `xoxb-`)
12. Save in .env as: `SLACK_BOT_TOKEN=xoxb_xxxxx`

**Also create #launches channel**:
1. In your Slack workspace, click "+"
2. Create channel: `launches`
3. Invite bot: Type `/invite @LaunchMindBot` in the channel

---

## 4. SendGrid API Key

**Link**: https://sendgrid.com/signup

**Step-by-Step**:
1. Go to https://sendgrid.com/signup
2. Sign up (free tier: 100 emails/day)
3. Verify your email (check inbox, click link)
4. In SendGrid dashboard, click Settings (⚙️)
5. Go to "API Keys"
6. Click "Create API Key"
7. Name: `LaunchMind`
8. **Permissions**: Check "Mail Send" only
9. Click "Create"
10. **Copy the key** (starts with `SG.`)
11. Save in .env as: `SENDGRID_API_KEY=SG.xxxxx`

**Verify sender email**:
1. In SendGrid, go to Settings → "Sender Authentication"
2. Click "Verify a Single Sender"
3. Email: `muhammadfaiza9876@gmail.com`
4. First Name: `Auto`
5. Last Name: `Test`
6. Click "Create"
7. **Check your email** - click the verification link

---

## 📋 .env File Template

Create `.env` file in launchmind/ directory with:

```
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_REPO=justfordeployment123/launchmind-fizan
SLACK_BOT_TOKEN=xoxb-YOUR_TOKEN_HERE
SENDGRID_API_KEY=SG.YOUR_KEY_HERE
SENDGRID_FROM_EMAIL=muhammadfaiza9876@gmail.com
SENDGRID_TO_EMAIL=muhammadfaiza9876@gmail.com
```

---

## 🚀 Quick Links Summary

| Service | Link | Key Format |
|---------|------|-----------|
| **OpenAI** | https://platform.openai.com/account/api-keys | `sk-proj-...` |
| **GitHub Token** | https://github.com/settings/tokens | `ghp_...` |
| **Slack Apps** | https://api.slack.com/apps | `xoxb-...` |
| **SendGrid** | https://sendgrid.com/signup | `SG....` |

---

## ⏱️ Time to Get All Keys

- OpenAI: ✅ You already have it (0 min)
- GitHub: 3 minutes
- Slack: 5 minutes
- SendGrid: 5 minutes

**Total: ~13 minutes**

Then just copy-paste into `.env` and run `python main.py`!

---

## ✅ Checklist

After getting all keys:

```
[ ] OpenAI key in .env (OPENAI_API_KEY)
[ ] GitHub token in .env (GITHUB_TOKEN)
[ ] GitHub repo created and PUBLIC (launchmind-fizan)
[ ] Slack bot token in .env (SLACK_BOT_TOKEN)
[ ] Slack #launches channel created
[ ] Slack bot invited to #launches
[ ] SendGrid API key in .env (SENDGRID_API_KEY)
[ ] SendGrid sender verified
[ ] .env file saved in launchmind/ directory
[ ] Ready to run: python main.py
```
