import sys
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel("gemini-1.5-flash")
agent = Agent(model, system_prompt="Check the following diff for vulnerabilities in accordance with OWASP Top Ten. Keep it one sentence.")

def analyze_diff(file_path):
    with open(file_path, 'r') as f:
        diff_content = f.read()
    print("Diff: ")

    print(diff_content, '\n')

    print("Analyzing diff for vulnerabilities...")
    res = agent.run_sync(user_prompt=diff_content)
    print(res.data)

if __name__ == "__main__":
    analyze_diff(sys.argv[1])
