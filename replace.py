import sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('CEO', 'Strategy')
content = content.replace('CFO', 'Salary')
content = content.replace('HR', 'Culture')
content = content.replace('ceo', 'strategy')
content = content.replace('cfo', 'salary')
content = content.replace('hr', 'culture')

with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.write(content)
