# 🐛 Debug Mode - How to See All Errors

## ✅ Issue Fixed: Gemini PDF Upload

The error you reported has been **FIXED**:
- Changed from `genai.upload_file()` to inline PDF bytes
- Now passes PDF directly to `generate_content()`
- No more "Missing required parameter ragStoreName" error

**File Modified:** `src/parsers.py`

---

## 🚀 Running with Error Visibility

### Method 1: Simple Debug Mode (Recommended)

Open a terminal and run:
```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
source .venv/bin/activate
streamlit run app.py
```

**Benefits:**
- ✅ All errors print to terminal immediately
- ✅ Easy to read and debug
- ✅ Press Ctrl+C to stop

---

### Method 2: Using Debug Script

```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
./run_debug.sh
```

**Benefits:**
- ✅ Same as Method 1
- ✅ Adds helpful startup messages
- ✅ Confirms environment is activated

---

### Method 3: With Log File (Best for Long Sessions)

```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
source .venv/bin/activate
streamlit run app.py 2>&1 | tee debug.log
```

**Benefits:**
- ✅ Errors visible in terminal
- ✅ Also saved to `debug.log` file
- ✅ Can review errors later

---

## 🎯 What to Do Now

### Step 1: Start App in Debug Mode
```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
source .venv/bin/activate
streamlit run app.py
```

### Step 2: Watch Terminal for Errors
- Terminal will show all errors in real-time
- Look for any red text or tracebacks
- Python errors will be clearly visible

### Step 3: Test Resume Upload
1. Open browser: http://localhost:8501
2. Go to "🎯 Live Demo" page
3. Upload a resume PDF
4. Watch terminal for any errors
5. Verify parsing works

### Step 4: Report Any New Errors
If you see any errors:
1. Copy the full error message from terminal
2. Share it with me
3. I'll fix it immediately

---

## 🔍 What Errors Look Like

### Example of a Python Error:
```
Traceback (most recent call last):
  File "/path/to/file.py", line 123, in function_name
    some_code()
TypeError: some error message
```

### Example of a Streamlit Error:
```
2025-10-17 12:34:56.789 ERROR: [Exception in app]
Traceback (most recent call last):
  ...
```

### Example of API Error:
```
openai.error.RateLimitError: You exceeded your quota
anthropic.APIError: Invalid API key
google.api_core.exceptions.GoogleAPIError: ...
```

**All of these will now be visible in your terminal!**

---

## 🛑 How to Stop the App

**Press:** `Ctrl + C` in the terminal

Or from another terminal:
```bash
pkill -f "streamlit run app.py"
```

---

## 📊 Current Status

### ✅ Fixed Issues:
1. **Gemini PDF Upload** - Changed to inline bytes method
2. **Package Installation** - All 107 packages installed
3. **Virtual Environment** - Created and activated
4. **Configuration** - All API keys loaded

### ✅ Working APIs:
- Gemini (Google AI) - FREE, for PDF parsing
- Claude (Anthropic) - For matching logic

### ⚠️ Known Issues:
- OpenAI needs billing (not critical, Claude is fallback)

---

## 🧪 Quick Tests Before Starting

Test that everything loads:
```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
source .venv/bin/activate

# Test imports
python3 -c "from src.parsers import ResumeParser; print('✅ Parser OK')"
python3 -c "from src.matcher import ResumeMatcher; print('✅ Matcher OK')"
python3 -c "from config.settings import get_settings; print('✅ Config OK')"
```

All should print "✅ OK"

---

## 💡 Pro Tips

### Tip 1: Keep Terminal Visible
When testing the app, keep the terminal window visible next to your browser so you can see errors immediately.

### Tip 2: Refresh After Code Changes
If we fix another error, you'll need to:
1. Press Ctrl+C to stop
2. Restart with `streamlit run app.py`
3. Browser will auto-refresh

### Tip 3: Check Terminal First
If something doesn't work in the UI:
1. Look at terminal immediately
2. Error message will tell us exactly what's wrong
3. Much faster than guessing!

### Tip 4: Save Error Messages
If you see an error:
1. Select and copy the entire error from terminal
2. Paste it to me
3. Include what you were doing when it happened

---

## 🎬 Ready to Start?

Run this command now:
```bash
cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher && source .venv/bin/activate && streamlit run app.py
```

Then:
1. Watch terminal for any startup errors
2. Open browser to http://localhost:8501
3. Try uploading a resume
4. Report any errors you see

**All errors will now be visible!** 🎉
