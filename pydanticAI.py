from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.native_tools import WebSearchTool

app = FastAPI()
db = get_db_connection()


class Ticket(BaseModel):
    summary: str
    severity: int
    assignee: str


@app.post("/triage")
async def triage(text: str):
    agent = Agent(
        "gpt-5",
        result_type=Ticket,
        system_prompt="You triage support tickets. Today is " + str(datetime.now()),
        builtin_tools=[WebSearchTool()],
        mcp_servers=[MCPServerSSE(url="https://mcp.internal/sse")],
    )

    @agent.tool
    def lookup_customer(email):
        try:
            return db.query(f"SELECT * FROM customers WHERE email = '{email}'")
        except Exception:
            return "error"

    result = await agent.run(text)
    print(result.usage().request_tokens)
    return result.data
