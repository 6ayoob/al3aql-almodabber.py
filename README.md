services:
  - type: web
    name: telegram-report-bot
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.3
      - key: PORT
        value: 1000
