import requests
import sys
import pprint
import os
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.markup import escape
from empyrion.options import options
from empyrion.helpers.timer import Timer
from empyrion.state.state import state

class СOllamaError(Exception):
  pass

class COllama:
  def __init__(self):
    self._timer = Timer()
    self._url = options.get("ollama.url", "http://localhost:11434")
    self._models = {
      'main': options.get("ollama.models.main"),
      'smart': options.get("ollama.models.smart"),
    }
    self._model = self._models['main']
    self._timeout = options.get("ollama.timeout", 600)
    self._options = {}
    if not self.isAlive():
      sys.exit("Ollama is not ready")

  def _modelOptions(self):
    if self._model not in self._options.keys():
      self._options[self._model] = options.get(f"ollama.models_options.{self._model}", {})
    return self._options[self._model]

  def isAlive(self):
    try:
      response = requests.get(f"{self._url}/api/tags", timeout=5)
      return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
      return False

  def switchToSmartModel(self):
    self._model = self._models['smart']

  def switchToMainModel(self):
    self._model = self._models['main']

  def printStat(self, result):
    table = Table()
    table.add_column("Tokens in", style="green4")
    table.add_column("Tokens out", style="turquoise4")
    table.add_row(str(result['prompt_eval_count']), str(result['eval_count']))
    Console().print(table)
    if 'thinking' in result:
      table = Table(expand=True)
      table.add_column("Thinking", style="deep_sky_blue4")
      table.add_row(escape(result['thinking']))
      Console().print(table)

  def query(self, prompt):
    try:
      rprint(f'Using model [bright_cyan]{self._model}[/bright_cyan]')
      self._timer.start()
      response = requests.post(
        f"{self._url}/api/generate",
        json={
          "model": self._model,
          "prompt": prompt,
          "stream": False,
          "options": self._modelOptions()
        },
        timeout=self._timeout
      )
      response.raise_for_status()
      elapsed = self._timer.stop()
      result = response.json()
      state.appendLLMQueryState(self._model, elapsed, result['prompt_eval_count'], result['eval_count'])
      self.printStat(result)
      state.showLLMState()
      return result.get("response", "")
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
      raise СOllamaError(f"Ollama query error: {str(e)}")

# ollama = COllama()
