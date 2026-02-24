
# FINAL WORKING LANGGRAPH + GROQ

from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
import os
import re
import dotenv

dotenv.load_dotenv()
#
# 1️⃣ SET YOUR GROQ API KEY
#

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
     model="openai/gpt-oss-120b"
)

#
# 2️⃣ DEFINE STATE
#

class State(TypedDict):
    question: str
    answer: str
    attempts: int


#
# 3️⃣ MATH NODE
#

def math_node(state: State):
    print("🔢 Running Math Node")

    try:
        # Extract math expression from sentence
        expression = re.findall(r"[0-9\+\-\*/\(\)\.]+", state["question"])
        expression = "".join(expression)

        if not expression:
            return {"answer": "No valid math expression found"}

        result = eval(expression)
        return {"answer": str(result)}

    except:
        return {"answer": "Invalid math expression"}


#
# 4️⃣ LLM NODE
#

def llm_node(state: State):
    print("🤖 Running LLM Node (Groq)")

    response = llm.invoke(state["question"])

    return {
        "answer": response.content,
        "attempts": state["attempts"] + 1
    }


#
# 5️⃣ ROUTER (START DECISION)
#

def router(state: State):
    print("🧭 Routing Question")

    if any(char.isdigit() for char in state["question"]):
        return "math_node"

    return "llm_node"


#
# 6️⃣ QUALITY CHECK (LOOP)
#

def quality_check(state: State):
    print("✅ Checking Answer Quality")

    if len(state["answer"]) < 20 and state["attempts"] < 3:
        print("⚠️ Answer too short, retrying...")
        return "llm_node"

    return END


#
# 7️⃣ BUILD GRAPH (CLEAN)
#

builder = StateGraph(State)

# Add real nodes only
builder.add_node("math_node", math_node)
builder.add_node("llm_node", llm_node)

# START → router
builder.add_conditional_edges("__start__", router)

# math → END
builder.add_edge("math_node", END)

# llm → quality check
builder.add_conditional_edges("llm_node", quality_check)

# Compile ONCE
graph = builder.compile()


#
# 8️⃣ RUN APP
#

if __name__ == "__main__":

    user_question = input("Ask something: ")

    result = graph.invoke({
        "question": user_question,
        "answer": "",
        "attempts": 0
    })

    print("\n🎉 Final Answer:")
    print(result["answer"])