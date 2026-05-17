# agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

load_dotenv()

from tools.csv_tool import analyze_sales_data
from tools.chart_tool import generate_chart
from tools.rag_tool import query_sales_report

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [analyze_sales_data, generate_chart, query_sales_report]

SYSTEM_PROMPT = """
You are SalesIQ, an intelligent sales analytics assistant for a B2B office 
equipment company. You help users understand sales data and generate insights.

Tools available:
1. analyze_sales_data — revenue, profit, trends, rep rankings, product comparisons
2. generate_chart — when user says show/plot/visualize/chart/graph
3. query_sales_report — strategy, goals, FY2025 targets, risks, qualitative questions

Always format numbers with Rs and commas. After every answer, add one proactive insight.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

memory = ConversationBufferWindowMemory(
    memory_key="chat_history", return_messages=True, k=6
)

agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent, tools=tools, memory=memory,
    verbose=True, handle_parsing_errors=True, max_iterations=5
)

def run_agent(user_message: str) -> dict:
    result = agent_executor.invoke({"input": user_message})
    output = result.get("output", "")
    chart_path = None
    for step in result.get("intermediate_steps", []):
        tool_name = step[0].tool if hasattr(step[0], "tool") else ""
        tool_output = step[1] if len(step) > 1 else ""
        if tool_name == "generate_chart" and isinstance(tool_output, str) and tool_output.endswith(".png"):
            chart_path = tool_output
    return {"output": output, "chart_path": chart_path}

if __name__ == "__main__":
    print("SalesIQ — Quick Test")
    r = run_agent("What is the total revenue?")
    print(r['output'])