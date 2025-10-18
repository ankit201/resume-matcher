#!/usr/bin/env python3
"""
Quick fix to add error handling to all dimension evaluation methods
"""

import re
from pathlib import Path

# Read the file
file_path = Path("src/llm_matcher.py")
content = file_path.read_text()

# Pattern to find all json.loads(response.content) calls in dimension methods
# We'll replace them with proper error handling

error_handling_code = '''try:
            result = json.loads(response.content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response (first 1000 chars): {response.content[:1000]}")
            result = {"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}'''

# Find and replace pattern: simple json.loads followed by return ScoreDimension
old_pattern = r'(\s+)result = json\.loads\(response\.content\)'
new_pattern = r'\1try:\n\1    result = json.loads(response.content)\n\1except json.JSONDecodeError as e:\n\1    print(f"❌ JSON error in {dimension}: {e}")\n\1    print(f"Response (first 1000): {response.content[:1000]}")\n\1    result = {"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}'

# Replace all occurrences except the one we already fixed in _evaluate_technical_skills
lines = content.split('\n')
in_technical_skills = False
fixed_lines = []

for i, line in enumerate(lines):
    if '_evaluate_technical_skills' in line:
        in_technical_skills = True
    elif line.strip().startswith('def _evaluate_'):
        in_technical_skills = False
    
    # Skip the one we already fixed
    if 'result = json.loads(response.content)' in line and not in_technical_skills:
        # Get indentation
        indent = len(line) - len(line.lstrip())
        spaces = ' ' * indent
        
        # Add try-except block
        fixed_lines.append(f'{spaces}try:')
        fixed_lines.append(f'{spaces}    result = json.loads(response.content)')
        fixed_lines.append(f'{spaces}except json.JSONDecodeError as e:')
        fixed_lines.append(f'{spaces}    print(f"❌ JSON decode error: {{e}}")')
        fixed_lines.append(f'{spaces}    print(f"Response (first 1000): {{response.content[:1000]}}")')
        fixed_lines.append(f'{spaces}    result = {{"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}}')
    else:
        fixed_lines.append(line)

# Write back
file_path.write_text('\n'.join(fixed_lines))
print(f"✓ Fixed {file_path}")
print("Added error handling to all dimension evaluation methods")
