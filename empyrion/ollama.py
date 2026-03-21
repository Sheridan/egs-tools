import requests
import sys
from string import Template
from empyrion.options import options


class COllama:
  def __init__(self):
    self.url = options.get("ollama.url", "http://localhost:11434")
    self.model = options.get("ollama.model", "translategemma:12b")
    self.system_prompt = Template(self.loadPrompt("system"))
    if not self.isAlive():
      sys.exit("Ollama is not ready")

  def loadPrompt(self, name):
    with open(f"templates/prompts/{name}.prompt", 'r', encoding='utf-8') as f:
      return f.read()

  def isAlive(self):
    try:
      response = requests.get(f"{self.url}/api/tags", timeout=5)
      return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
      return False

  def query(self, prompt):
    query_prompt = self.system_prompt.safe_substitute(
                    src_language=options.get("translation.src_language", "English"),
                    dst_language=options.get("translation.dst_language", "Russian"),
                    query_prompt=prompt
                  )
    try:
      response = requests.post(
        f"{self.url}/api/generate",
        json={
          "model": self.model,
          "prompt": query_prompt,
          "stream": False
        },
        timeout=120
      )
      response.raise_for_status()
      result = response.json()
      return result.get("response", "")
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
      raise Exception(f"Ollama query error: {str(e)}")

ollama = COllama()
