import os

with open('tests/test_smart_agents.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('CEO', 'Strategy')
c = c.replace('CFO', 'Salary')
c = c.replace('HR', 'Culture')
c = c.replace('ceo', 'strategy')
c = c.replace('cfo', 'salary')
c = c.replace('hr', 'culture')

with open('tests/test_smart_agents.py', 'w', encoding='utf-8') as f:
    f.write(c)
