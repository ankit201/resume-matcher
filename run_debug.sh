#!/bin/bash
# Debug mode runner for Resume Matcher
# Shows all errors in terminal for easy debugging

echo "🐛 Starting Resume Matcher in DEBUG mode"
echo "=========================================="
echo ""
echo "✅ All errors will be visible in this terminal"
echo "✅ Press Ctrl+C to stop the application"
echo "✅ Access at: http://localhost:8501"
echo ""
echo "Starting in 3 seconds..."
sleep 3

cd /home/FRACTAL/ankit.singh3/interviews/resume-matcher
source .venv/bin/activate
streamlit run app.py --server.headless true
