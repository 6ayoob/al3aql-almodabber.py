services:
  - type: web
    name: al3aql-almodabber
    env: python
    plan: free
    pythonVersion: 3.10.11
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
