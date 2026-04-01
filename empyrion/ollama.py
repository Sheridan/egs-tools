import requests
import sys
import pprint
import os
import re
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
    if not self.isAlive():
      sys.exit("Ollama is not ready")

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
    table = Table(expand=True)
    table.add_column("Tokens in", style="green4")
    table.add_column("Tokens out", style="turquoise4")
    table.add_row(str(result['prompt_eval_count']), str(result['eval_count']))
    Console().print(table)
    if 'thinking' in result:
      table = Table(expand=True)
      table.add_column("Thinking", style="deep_sky_blue4")
      table.add_row(escape(result['thinking']))
      Console().print(table)

  def _queryLog(self, system_prompt, user_prompt, current):
    if options.get("debug", False):
      table = Table(show_lines=True, expand=True)
      table.add_column("---"  , style="magenta", no_wrap=False, highlight=False)
      table.add_column("Debug", style="yellow" , no_wrap=False, highlight=False)
      table.add_row("System"  , escape(system_prompt))
      table.add_row("User"    , escape(user_prompt))
      table.add_row("Response", escape(current))
      Console().print(table)

  def _preparePrompt(self, prompt):
    return re.sub(r'\n{2,}', '\n\n', prompt)

  def query(self, system_prompt, user_prompt):
    system_prompt = self._preparePrompt(system_prompt)
    user_prompt = self._preparePrompt(user_prompt)
    try:
      rprint(f'Using model [bright_cyan]{self._model}[/bright_cyan]')
      self._timer.start()
      query = {
          "model": self._model,
          "stream": False,
          "options": options.get(f"ollama.models_options.{self._model}.api", {})
        }
      if options.get(f"ollama.models_options.{self._model}.accept_system_prompt", False):
        query['system'] = system_prompt
        query['prompt'] = user_prompt
      else:
        query['prompt'] = f'{system_prompt}\n{user_prompt}'
      # rprint(query)
      response = requests.post(
        f"{self._url}/api/generate",
        json=query,
        timeout=self._timeout
      )
      response.raise_for_status()
      elapsed = self._timer.stop()
      result = response.json()
      answer = result.get("response", "")
      state.appendLLMQueryState(self._model, elapsed, result['prompt_eval_count'], result['eval_count'])
      self.printStat(result)
      self._queryLog(system_prompt, user_prompt, answer)
      state.showLLMState()
      return answer
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
      raise СOllamaError(f"Ollama query error: {str(e)}")

# ollama = COllama()
