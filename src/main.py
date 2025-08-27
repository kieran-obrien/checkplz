#!/usr/bin/env python3
import os, requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv

load_dotenv()
console = Console()

def main():
  with open("./dummypkgdir/dummypkgbuild.txt", "r") as f:
    pkgbuild_content = f.read()
  console.print("[green]Reading PKGBUILD content...", style="bold")
  console.print("[yellow]Evaluating for security threats...", style="bold")
  console.print(get_ai_evaluation(pkgbuild_content))
  
def get_ai_evaluation(pkgbuild_content):
  prompt = f"Evaluate the following PKGBUILD content for security threats:\n\n{pkgbuild_content}\n\nProvide a detailed analysis and suggest whether the package is safe to be installed."
  groq_api_key = os.environ.get("GROQ_API_KEY")
  groq_url = "https://api.groq.com/openai/v1/chat/completions"
  groq_headers = {
      "Authorization": f"Bearer {groq_api_key}",
      "Content-Type": "application/json"
  }
  groq_data = {
    "model": "llama-3.3-70b-versatile",
    "temperature": 1,
    "messages": [
      {
        "role": "user",
        "content": prompt
      }
    ]
  }

  res = requests.post(groq_url, json=groq_data, headers=groq_headers)
  if res.status_code == 200:
    return res.json()['choices'][0]['message']['content']
  else:
    print("Error: Something went wrong during AI evaluation!", res.status_code, res.text)


if __name__ == "__main__":
    main()