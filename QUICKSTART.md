# 🚀 Quick Start Guide

Get up and running with TechCorp AI Resume Matcher in under 5 minutes!

## ⚡ Super Quick Start (For Demo)

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/resume-matcher.git
cd resume-matcher
./setup.sh

# 2. Add API keys
cp .env.example .env
# Edit .env with your OpenAI and Google AI keys

# 3. Run!
source .venv/bin/activate
streamlit run app.py
```

That's it! The app will open in your browser at http://localhost:8501

## 📋 Prerequisites

- **Python 3.9+** (Check with `python3 --version`)
- **API Keys**:
  - OpenAI API Key (Required) - [Get it here](https://platform.openai.com/api-keys)
  - Google AI API Key (Required) - [Get it here](https://makersuite.google.com/app/apikey)
  - Anthropic API Key (Optional) - [Get it here](https://console.anthropic.com/account/keys)

## 🔑 Getting API Keys

### OpenAI (Required)
1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Add $5-10 credits for testing

### Google AI (Required)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Get API Key" or "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Free tier includes generous quota

### Anthropic (Optional)
1. Go to https://console.anthropic.com/account/keys
2. Sign in or create account
3. Click "Create Key"
4. Copy the key (starts with `sk-ant-...`)
5. Optional for Claude comparison

## 🛠️ Step-by-Step Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/resume-matcher.git
cd resume-matcher
```

### 2. Run Setup Script

The setup script will:
- Check Python version
- Install UV package manager (if needed)
- Create virtual environment
- Install all dependencies
- Pre-download AI models

```bash
chmod +x setup.sh
./setup.sh
```

**Expected output:**
```
🚀 Resume Matcher - Setup Script (UV Edition)
==============================================

📋 Checking Python version...
Found Python 3.11.5
✅ Python 3.11.5 detected

📦 Checking for UV package manager...
✅ UV already installed (0.1.5)

🔧 Creating virtual environment with UV...
✅ Virtual environment created at .venv/

📥 Installing dependencies with UV...
This may take a few minutes...
✅ Dependencies installed successfully

📚 Pre-downloading embedding model...
✅ Embedding model cached

==============================================
✅ Setup Complete!
```

### 3. Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env
# OR
vim .env
# OR
code .env  # if you have VS Code
```

**Minimal `.env` configuration:**
```env
# REQUIRED
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=AIza-your-google-key-here

# OPTIONAL
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 4. Run the Application

**Option A: With virtual environment activation**
```bash
source .venv/bin/activate
streamlit run app.py
```

**Option B: Direct with UV (no activation needed)**
```bash
uv run streamlit run app.py
```

The app will automatically open in your browser at: **http://localhost:8501**

## 📱 Using the Application

### Quick Demo (1 minute)

1. **Go to Live Demo page** (in sidebar)
2. **Upload a sample resume PDF**
   - Don't have one? Use: `data/resumes/sample.pdf` (you'll need to create this)
3. **Paste or load job description**
   - Sample provided in: `data/job_descriptions/senior_ai_engineer.txt`
4. **Click "Match Resume to Job"**
5. **View detailed results!**

### Explore Other Features

- **📊 Executive Dashboard** - View ROI calculator and KPIs
- **⚖️ Bias Analysis** - Check fairness metrics and compliance
- **📦 Batch Processing** - Screen multiple resumes at once

## 🐛 Troubleshooting

### "UV not found" Error

If UV installation fails:
```bash
# Manual UV installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Verify
uv --version
```

### "Import Error: google.generativeai"

Dependencies not installed properly:
```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install --force-reinstall -e .
```

### "API Key Error"

1. Check `.env` file exists and has correct keys
2. Verify keys don't have quotes: ❌ `"sk-..."` → ✅ `sk-...`
3. Test API keys:
```bash
# OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Google AI
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
```

### "Streamlit not found"

Virtual environment not activated:
```bash
source .venv/bin/activate
streamlit run app.py
```

Or use UV:
```bash
uv run streamlit run app.py
```

### Port Already in Use

Streamlit default port (8501) is occupied:
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Slow First Run

First time running:
- Downloads embedding model (~100MB)
- Initializes Streamlit cache
- Normal behavior, subsequent runs are fast

## 🧪 Testing the Setup

### Test 1: Check Python and Dependencies
```bash
source .venv/bin/activate
python -c "import streamlit; import openai; import google.generativeai; print('✅ All imports successful!')"
```

### Test 2: Verify API Keys
```bash
source .venv/bin/activate
python -c "from config.settings import get_settings; s = get_settings(); print('✅ OpenAI:', 'OK' if s.openai_api_key else 'MISSING'); print('✅ Gemini:', 'OK' if s.google_api_key else 'MISSING')"
```

### Test 3: Test Parsing
```bash
source .venv/bin/activate
python -c "from src.parsers import ResumeParser; print('✅ Parser initialized!')"
```

## 📊 Sample Data

For testing, you'll need:

### Resume PDFs
Place in `data/resumes/`:
- Use your own resume
- Or create sample resumes
- Or download from [sample-resumes.com](https://www.sample-resumes.com/)

### Job Descriptions
Provided sample: `data/job_descriptions/senior_ai_engineer.txt`

Or create your own:
```bash
nano data/job_descriptions/my_job.txt
```

## 🎯 Next Steps

After setup:

1. **Try Live Demo** - Test with single resume
2. **Explore Dashboard** - See ROI calculator
3. **Test Batch Processing** - Upload 5-10 resumes
4. **Check Bias Analysis** - Review fairness metrics
5. **Customize Settings** - Edit `config/config.yaml`

## 📚 Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Migration Guide**: [MIGRATION_NOTES.md](MIGRATION_NOTES.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Reference**: [docs/API.md](docs/API.md)

## 💬 Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/yourusername/resume-matcher/issues)
- **Email**: support@techcorp.com
- **Slack**: #resume-matcher channel

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Repository cloned
- [ ] `setup.sh` executed successfully
- [ ] UV package manager working
- [ ] Dependencies installed
- [ ] `.env` file created with API keys
- [ ] OpenAI API key configured
- [ ] Google AI API key configured
- [ ] Streamlit app running
- [ ] Browser opened to http://localhost:8501
- [ ] Sample resume uploaded and tested
- [ ] Match analysis completed successfully

If all boxes are checked, you're ready to go! 🎉

---

<div align="center">
  <strong>Happy Matching! 🎯</strong>
  <br>
  <sub>Questions? Check the troubleshooting section or open an issue</sub>
</div>
