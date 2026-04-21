import os
import re
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match old scenario args loosely
    pattern = r'(budget_million_usd=[\d\.]+.*?team_readiness=\d+)'
    new_args = 'experience_years=5, tech_test_score=85, avg_months_per_job=24, glassdoor_score=4.5, expected_salary=80000'
    content = re.sub(pattern, new_args, content, flags=re.DOTALL)
    
    # Other potential variants
    pattern2 = r'budget_million_usd=[\d\.]+,[ \n]*expected_roi_percent=[\d\.\-]+,[ \n]*risk_level=\d+'
    content = re.sub(pattern2, new_args, content)
    
    pattern3 = r'budget_million_usd=[\d\.]+,[ \n]*expected_roi_percent=[\d\.\-]+,[ \n]*risk_level=\d+,[ \n]*team_readiness=\d+'
    content = re.sub(pattern3, new_args, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for file in glob.glob('tests/*.py'):
    fix_file(file)

