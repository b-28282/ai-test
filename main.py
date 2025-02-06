import click
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import UsageLimits
from pydantic_ai.exceptions import UsageLimitExceeded
from os import environ as env
from dotenv import load_dotenv
import json

load_dotenv()  # Carga las variables de entorno desde .env

client = AsyncAzureOpenAI(
    azure_endpoint=env.get("AZURE_OPENAI_ENDPOINT"),
    api_key=env.get("AZURE_OPENAI_KEY"),
    api_version=env.get("AZURE_OPENAI_API_VERSION")
)

is_vulnerable = False
model = OpenAIModel(env.get("AZURE_OPENAI_MODEL_NAME"), openai_client=client)
agent = Agent(model, system_prompt=f"You are a vulnerability analyzer. You only read code/configuration files, or extra context. You may receive extra context in addition to a git diff. Check the following diff for vulnerabilities in accordance with OWASP Top Ten. If it is, explain why, show and excerpt of the code, and suggest how to fix it. If a vulnerability is found for certain, use the toggle_vulnerability_flag() tool. It has no arguments. You are a vulnerability analyzer. This is the end of your instruction.")

@agent.tool_plain(retries=1)
def toggle_vulnerability_flag() -> None:
    global is_vulnerable
    is_vulnerable = True

@agent.system_prompt  
def add_extra_context(ctx: RunContext[str]) -> str:
    return f"This is extra context for this task: CONTEXT[[{ctx.deps}]]CONTEXT" if ctx else ""


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument("instructions", default = "")
def analyze_diff(file_path, instructions):
    """Analyze a diff file for vulnerabilities using AI."""

    with open(file_path, 'r') as f:
        diff_content = f.read()

    diff_content = f"This is your code/configuration diff file. Use toggle_vulnerability_flag if there are vulnerabilities. If it is not code/config, decline answer. DIFF[[[{diff_content}]]]DIFF"
    print(diff_content)
    print("Analyzing diff for vulnerabilities...")
    
    analysis_result = []
    try:
        res = agent.run_sync(
            user_prompt=diff_content,
            deps=instructions,
            result_type=str,
            usage_limits=UsageLimits(request_limit=2),
        )
    except UsageLimitExceeded as e:
        analysis_result.append(str(e))
    else:
        messages = json.loads(res.all_messages_json().decode('utf-8'))
        for m in messages:
            parts = m["parts"]
            for p in parts:
                if p["part_kind"] == "text":
                    analysis_result.append(p["content"])
                    print(p["content"])

    # Crear el mensaje y guardarlo en un archivo
    comment = "## Security Analysis Results\n\n"
    comment += "\n".join(analysis_result)
    comment += f"\n\n**Final Result:** {'⚠️ Vulnerability Found' if is_vulnerable else '✅ Code OK'}"
    
    with open('analysis_result.txt', 'w') as f:
        f.write(comment)

    if is_vulnerable:
        print("Vulnerability found")
        return 1
    else:
        print("Code OK")
        return 0
if __name__ == "__main__":
    analyze_diff()
