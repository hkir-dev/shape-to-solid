from main import  llm_architect

# Simple connectivity check
try:
    response = llm_architect.call([{"role": "user", "content": "Ping"}])
    print("Connection to GitHub Copilot successful!")
except Exception as e:
    print(f"Connection failed. Check your GITHUB_COPILOT_TOKEN. Error: {e}")