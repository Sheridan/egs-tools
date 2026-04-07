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
from empyrion.statistics.statistics import statistics
from empyrion.helpers.filesystem import append_to_file
from empyrion.helpers.strings import estimate_tokens

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
    self._max_query_tryes=options.get("ollama.max_tryes", 16)
    if not self.isAlive():
      sys.exit("Ollama is not ready")

  def isAlive(self):
    try:
      response = requests.get(f"{self._url}/api/tags", timeout=5)
      return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
      return False

  def switchToSmartModel(self):
    self._model = self._models['smart'] if  self._models['smart'] != "none" else self._models['main']

  def switchToMainModel(self):
    self._model = self._models['main']

  def _log(self, system_prompt, user_prompt, result):
    delimiter = ':'*80
    part_delimiter = '-'*20
    texts = [
      delimiter,
      f'{part_delimiter}== model: {self._model} =={part_delimiter}',
      f'{part_delimiter}== system prompt ({len(system_prompt)}), estimate tokens: {estimate_tokens(system_prompt)} =={part_delimiter}',
      system_prompt,
      f'{part_delimiter}== user prompt ({len(user_prompt)}), estimate tokens: {estimate_tokens(user_prompt)} =={part_delimiter}',
      user_prompt,
      f'{part_delimiter}== thinking ({len(result['thinking']) if 'thinking' in result else '-'}) =={part_delimiter}',
      result['thinking'] if 'thinking' in result else '[without thinking]',
      f'{part_delimiter}== answer ({len(result['response'])}) =={part_delimiter}',
      result['response'],
      delimiter
    ]
    append_to_file('ollama', '\n'.join(texts))

  def printStat(self, result):
    if not self._isMetaInResult(result):
      return
    rprint(f"Tokens in: [green4]{result['prompt_eval_count']}[/green4]; out: [turquoise4]{result['eval_count']}[/turquoise4]")
    if 'thinking' in result:
      table = Table(expand=True)
      table.add_column("Thinking", style="deep_sky_blue4")
      table.add_row(escape(result['thinking']))
      Console().print(table)

  def _queryLog(self, system_prompt, user_prompt, answer):
    if options.get("debug", False):
      table = Table(show_lines=True, expand=True)
      table.add_column("---"  , style="magenta", no_wrap=False, highlight=False)
      table.add_column("Debug", style="yellow" , no_wrap=False, highlight=False)
      table.add_row(f"System\nLen: {len(system_prompt)}\nEst Tns\n{estimate_tokens(system_prompt)}", escape(system_prompt))
      table.add_row(f"User\nLen: {len(user_prompt)}\nEst Tns\n{estimate_tokens(user_prompt)}"    , escape(user_prompt))
      table.add_row(f"Response\nLen: {len(answer)}\nEst Tns\n{estimate_tokens(answer)}"          , escape(answer))
      Console().print(table)

  def _isMetaInResult(self, result):
    return 'prompt_eval_count' in result and 'eval_count' in result

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
      # rprint(system_prompt)
      # rprint(user_prompt)
      response = requests.post(
        f"{self._url}/api/generate",
        json=query,
        timeout=self._timeout
      )
      response.raise_for_status()
      elapsed = self._timer.stop()
      result = response.json()
      # rprint(result)
      answer = result.get("response", "")
      if self._isMetaInResult(result):
        statistics.appendLLMQueryMetrics(self._model, elapsed, result['prompt_eval_count'], result['eval_count'])
      self.printStat(result)
      self._queryLog(system_prompt, user_prompt, answer)
      self._log(system_prompt, user_prompt, result)
      return answer
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
      raise СOllamaError(f"Ollama query error: {str(e)}")

# ollama = COllama()
