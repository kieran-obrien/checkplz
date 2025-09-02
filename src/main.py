#!/usr/bin/env python3
import os, requests, tempfile, subprocess, os, sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv


load_dotenv()
console = Console()


def main():
  pkgname = check_argv()
  console.print("[green]Reading PKGBUILD content...", style="bold")
  console.print("[yellow]Evaluating for security threats...", style="bold")
  evaluate_package(pkgname, get_ai_evaluation)


def check_argv():
    if len(sys.argv) < 2:
        pkgname = input("Enter package name: ").strip()
    else:
        pkgname = sys.argv[1]
    if len(sys.argv) > 2:
      console.print(f"Extra arguments ignored, using {sys.argv[1]}")
    return pkgname
  
   
def evaluate_package(pkgname, eval_callback_function):
  with tempfile.TemporaryDirectory() as tmpdir:
    pkg_clone_dir = clone_aur_repo(tmpdir, pkgname)
    pkgbuild_path = os.path.join(pkg_clone_dir, "PKGBUILD")
    if not os.path.isfile(pkgbuild_path):
      console.print(f"PKGBUILD not found. Package {pkgname} may not exist in AUR.", style="red")
      return sys.exit(1)
    console.print("The following files were found:", style="bold")
    console.print(os.listdir(pkg_clone_dir), style="green")
    console.print("\n\n")
    res = (eval_callback_function(pkg_clone_dir))
    console.print("\n\n")
    console.print(Panel(Text(res, style="white on black"), title="Evaluation", subtitle="ALWAYS READ THE PKGBUILD", border_style="blue"))


def clone_aur_repo(tmpdir, pkgname):
  pkg_clone_dir = os.path.join(tmpdir, pkgname)
  try:
    subprocess.run(
        ["git", "clone", f"https://aur.archlinux.org/{pkgname}.git", pkg_clone_dir],
        check=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )
  except FileNotFoundError:
      console.print("[red]Error: 'git' is not installed or not found in PATH.[/]")
      sys.exit(1)
  except subprocess.CalledProcessError:
      console.print("[red]Error: git clone failed. Check network connection?[/]")
      sys.exit(1)
  return pkg_clone_dir


def should_include(fname, root, base_dir):
    if fname == "PKGBUILD":
        return True
    if fname.endswith(".install"):
        return True
    if fname.endswith(".sh") and root == base_dir:
        return True
    return False


def get_ai_evaluation(pkg_clone_dir):
  eval_content = ""

  for root, dirs, files in os.walk(pkg_clone_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".git")]
        for fname in files:
            if should_include(fname, root, pkg_clone_dir):
                file_path = os.path.join(root, fname)
                try:
                    with open(file_path, "r", errors="ignore") as f:
                        relative_path = os.path.relpath(file_path, pkg_clone_dir)
                        eval_content += f"<-- {relative_path} -->\n"
                        eval_content += f.read() + "\n"
                except Exception as e:
                    eval_content += f"<-- {fname} (skipped due to error: {e}) -->\n"  

  console.print(Panel(Text(eval_content, style="white on black"), title="AUR Package Content", subtitle="Sent for AI Evaluation", border_style="blue"))

  prompt = f"Evaluate the following PKGBUILD content for security threats:\n\n{eval_content}\n\nProvide a detailed analysis and suggest whether the package is safe to be installed."
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