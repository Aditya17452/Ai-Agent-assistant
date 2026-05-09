import os 
from groq import Groq 
from dotenv import load_dotenv 
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Minimal fix: correct the malformed chat initialization (syntax error)
chat = [{
    "role": "system",
    "content": (
        "You are an AI agent. You have access to these tools:\n\n"
        "1. get_weather(city) - use when user asks about weather\n"
        "2. calculate(expression) - use when user asks to calculate something\n"
        "3. get_joke() - use when user wants a joke\n"
        "4. answer(text) - use when no tool is needed, just answer directly\n\n"
        "You MUST respond in EXACTLY this format, nothing else:\n"
        "TOOL: tool_name | argument\n\n"
        "Examples:\n"
        "TOOL: get_weather | Delhi\n"
        "TOOL: calculate | 15 * 4 + 2\n"
        "TOOL: get_joke | none\n"
        "TOOL: answer | The capital of India is New Delhi\n\n"
        "Only one line. No explanation. No extra text."
    )
}]


import requests

def get_weather(city):
    api_key = "e306d4e650d424d9b9b02d11b1f46c91"
    
    # http ki jagah https lagao
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("cod") == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"{city} mein aaj {temp}°C hai, {desc}"
        else:
            return f"City nahi mili: {data.get('message', 'unknown error')}"
    
    except requests.exceptions.ConnectTimeout:
        return "Weather API se connect nahi ho pa raha — internet check karo ya thoda wait karo"
    
    except requests.exceptions.ConnectionError:
        return "Connection error — network check karo"
    
    except Exception as e:
        return f"Kuch error aaya: {str(e)}"

def calculate(expression):
    try:
        result = eval(expression)
        return f"Answer: {result}"
    except:
        return "Invalid math expression"

def get_joke():
    return "Why do programmers prefer dark mode? Because light attracts bugs!"

def llm_output(prompt):
    chat.append({"role":"user","content":prompt})
    r=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat ,temperature=0,
        max_tokens=500 
    )
    return r.choices[0].message.content


def parse_tool_output(llm_output):
    # llm_output = "TOOL: get_weather | Mumbai"

    # step 1: "TOOL: " hata do
    cleaned = llm_output.replace("TOOL: ", "")
    # cleaned = "get_weather | Mumbai"

    # step 2: " | " pe split karo
    parts = cleaned.split(" | ")
    # parts = ["get_weather", "Mumbai"]

    # step 3: tool name aur argument alag karo
    tool_name = parts[0].strip()   # "get_weather"
    argument  = parts[1].strip() if len(parts) > 1 else "none"  # "Mumbai"

    return tool_name, argument


def execute_tool(tool_name, argument):
    
    if tool_name == "get_weather":
        return get_weather(argument)
    
    elif tool_name == "calculate":
        return calculate(argument)
    
    elif tool_name == "get_joke":
        return get_joke()          # no argument needed
    
    elif tool_name == "answer":
        return argument            # argument itself IS the answer
    
    else:
        return f"Unknown tool: {tool_name}"
    

def run_agent(user_input):
    if user_input.lower() == "exit":
        return "Bye"
    r=llm_output(user_input)
    tool_name, argument = parse_tool_output(r)
    tool_result = execute_tool(tool_name, argument)
    chat.append({"role":"assistant","content":r})
    print(f"Tool Result: {tool_result}")
    return tool_result

def chat_history():
    return chat


if __name__=="__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        run_agent(user_input)   
    