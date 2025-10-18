# 🔑 Quick Setup: Add Your API Keys

**⏱️ Takes 5 minutes | 3 Simple Steps**

---

## 📍 Step 1: Open Your `.env` File

The `.env` file is located here:
```
/home/FRACTAL/ankit.singh3/interviews/resume-matcher/.env
```

Open it with any text editor:
```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
nano .env
# or
code .env
# or
vim .env
```

---

## 🔑 Step 2: Get Your API Keys

### OpenAI API Key (Required)

1. **Go to:** https://platform.openai.com/api-keys
2. **Click:** "Create new secret key"
3. **Name it:** "Resume Matcher" (optional)
4. **Copy the key** (starts with `sk-proj-...`)
5. **Paste in .env** like this:

```bash
OPENAI_API_KEY=sk-proj-abc123xyz789...
```

**💰 Cost:** ~$0.03-0.05 per resume  
**💳 Billing:** https://platform.openai.com/account/billing

---

### Google AI API Key (Required)

1. **Go to:** https://aistudio.google.com/apikey
2. **Click:** "Get API key" → "Create API key"
3. **Select:** Create API key in new project (or existing)
4. **Copy the key** (starts with `AIzaSy...`)
5. **Paste in .env** like this:

```bash
GOOGLE_API_KEY=AIzaSyAbc123Xyz789...
```

**💰 Cost:** FREE (within generous quota)  
**📊 Quota:** 15 requests/min, 1500/day

---

### Anthropic API Key (Optional)

**Note:** Only needed if you want to compare with Claude

1. **Go to:** https://console.anthropic.com/account/keys
2. **Click:** "Create Key"
3. **Name it:** "Resume Matcher"
4. **Copy the key** (starts with `sk-ant-api03-...`)
5. **Paste in .env** like this:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-abc123xyz789...
```

**💰 Cost:** ~$0.04-0.06 per resume  
**💳 Billing:** https://console.anthropic.com/account/billing

---

## ✅ Step 3: Verify Your Setup

After adding your keys, test everything works:

```bash
# Test your configuration
./test_setup.py

# If all tests pass, run the app
streamlit run app.py
```

---

## 📝 Your `.env` File Should Look Like This:

```bash
# ============================================================================
# AI RESUME MATCHER - ENVIRONMENT CONFIGURATION
# ============================================================================

# ----------------------------------------------------------------------------
# 🔑 LLM API KEYS (REQUIRED)
# ----------------------------------------------------------------------------

# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE_abc123xyz789...

# Google AI API Key (REQUIRED)
GOOGLE_API_KEY=AIzaSyYOUR_ACTUAL_KEY_HERE_abc123xyz789...

# Anthropic API Key (OPTIONAL)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE_abc123xyz789...

# ----------------------------------------------------------------------------
# 🤖 MODEL CONFIGURATION
# ----------------------------------------------------------------------------

OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.5-flash
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ... rest of configuration (already set up) ...
```

---

## 🎯 Quick Test Commands

### Test Individual APIs

**Test OpenAI:**
```python
python3 -c "
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-4o',
    messages=[{'role': 'user', 'content': 'Say hello'}],
    max_tokens=10
)
print('✅ OpenAI works!', response.choices[0].message.content)
"
```

**Test Gemini:**
```python
python3 -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content('Say hello')
print('✅ Gemini works!', response.text)
"
```

**Test Anthropic:**
```python
python3 -c "
from anthropic import Anthropic
import os
from dotenv import load_dotenv
load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
message = client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Say hello'}]
)
print('✅ Anthropic works!', message.content[0].text)
"
```

---

## 🔒 Security Reminders

**✅ DO:**
- Keep `.env` in your project root
- Add real keys with no quotes or spaces
- Test with `./test_setup.py`
- Keep `.env` private (never share)

**❌ DON'T:**
- Commit `.env` to git (already in .gitignore)
- Share keys in screenshots
- Use keys in code files directly
- Share your `.env` file with anyone

---

## ❓ Troubleshooting

### "Cannot find .env file"
**Solution:** Make sure you're in the project root:
```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
pwd  # Should show the project path
ls .env  # Should see .env file
```

### "Invalid API Key"
**Solutions:**
1. Check for typos (copy-paste keys)
2. Remove any spaces before/after key
3. Don't add quotes around the key
4. Regenerate key from provider dashboard

### "API Key format incorrect"
**Check formats:**
- OpenAI: `sk-proj-...` (48-51 chars)
- Google: `AIzaSy...` (39 chars)
- Anthropic: `sk-ant-api03-...` (60+ chars)

### "Rate limit exceeded"
**Solutions:**
1. Wait 60 seconds and try again
2. Check your API quota on provider dashboard
3. Upgrade to paid tier if needed

### ".env not loading"
**Solutions:**
```bash
# Make sure python-dotenv is installed
pip install python-dotenv

# Check file permissions
chmod 600 .env

# Verify file content
cat .env | head -20
```

---

## 💰 Expected Costs (for budgeting)

### Free Tier Limits
- **Gemini:** 1,500 requests/day (more than enough for testing)
- **OpenAI:** Paid only (but very cheap)
- **Anthropic:** Paid only (optional)

### Typical Usage Costs

**Testing Phase (100 resumes):**
- Resume parsing (Gemini): $0 (free tier)
- Matching (OpenAI): ~$3-5
- **Total: ~$3-5**

**Demo Day (10-20 resumes):**
- Resume parsing: $0 (free tier)
- Matching: ~$0.30-1.00
- **Total: Under $1**

**Production (1000 resumes/month):**
- Resume parsing: $0 (free tier)
- Matching: ~$30-50
- **Total: ~$30-50/month**

**vs. Traditional Vendor:** $2,000,000/year  
**Savings:** 99.7% cost reduction

---

## 🎓 Understanding Your .env File

### What Gets Used Where

```
.env File
│
├── OPENAI_API_KEY
│   └── Used in: src/llm_adapters/openai_adapter.py
│       └── For: Resume-job matching, deep analysis
│
├── GOOGLE_API_KEY
│   └── Used in: src/parsers.py, src/llm_adapters/gemini_adapter.py
│       └── For: PDF resume parsing, structured extraction
│
└── ANTHROPIC_API_KEY (optional)
    └── Used in: src/llm_adapters/anthropic_adapter.py
        └── For: Alternative matching comparison
```

### How Configuration Loads

```
1. Application starts
   ↓
2. config/settings.py loads .env
   ↓
3. Pydantic validates all settings
   ↓
4. Settings cached with @lru_cache()
   ↓
5. LLM adapters get keys via get_settings()
   ↓
6. APIs are ready to use!
```

---

## ✅ Final Checklist

Before you start:

- [ ] **Created `.env` file** (already done ✅)
- [ ] **Obtained OpenAI API key** - https://platform.openai.com/api-keys
- [ ] **Obtained Google AI API key** - https://aistudio.google.com/apikey
- [ ] **Added both keys to `.env`** (replace "your_xxx_key_here")
- [ ] **Saved `.env` file**
- [ ] **Ran `./test_setup.py`** - All tests pass?
- [ ] **Added 3-5 sample resumes** to `data/resumes/`
- [ ] **Ready to run:** `streamlit run app.py`

---

## 🚀 You're All Set!

Once your keys are in `.env`, you're ready to:

1. **Test Setup:**
   ```bash
   ./test_setup.py
   ```

2. **Launch Application:**
   ```bash
   streamlit run app.py
   ```

3. **Access UI:**
   - Open browser to: http://localhost:8501
   - Upload a resume on "Live Demo" page
   - See the magic happen! ✨

---

## 📞 Need Help?

**API Key Issues:**
- OpenAI Support: https://help.openai.com/
- Google AI Help: https://ai.google.dev/gemini-api/docs/api-key
- Anthropic Support: https://support.anthropic.com/

**Configuration Issues:**
- Check: `API_VERIFICATION.md` for detailed syntax
- Check: `README.md` for full documentation
- Check: `QUICKSTART.md` for fast walkthrough
- Run: `./test_setup.py` for diagnostics

---

<div align="center">

## 🎯 Ready to Build Something Amazing!

**Your keys → `.env` → Test → Launch → Demo → Success!**

</div>
