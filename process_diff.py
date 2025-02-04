import sys
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel("gemini-1.5-flash")
agent = Agent(model, system_prompt="Check the following diff for vulnerabilities in accordance with OWASP Top Ten. If it is, explain why. Keep it one sentence. If a vulnerability is certainly found, use toggle_vulnerability_flag function. It has no arguments. If you need more context, do NOT toggle.")

is_vulnerable = False

@agent.tool_plain()
def toggle_vulnerability_flag() -> None:
    global is_vulnerable
    is_vulnerable = True

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

    if is_vulnerable:
        raise Exception("Code vulnerable!")
    else:
        print("Code OK")
