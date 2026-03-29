import requests
import sys
import pprint
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.markup import escape
from empyrion.options import options
from empyrion.helpers.timer import Timer


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
    self._options = {
       "temperature": options.get("temperature", 0.4),
        "top_p": options.get("top_p", 0.9)
    }
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
    q_time = self._timer.get()
    table = Table(expand=True)
    table.add_column("Query time"   , style="yellow"        )
    table.add_column("Query tokens" , style="bright_magenta")
    table.add_column("Reply tokens" , style="bright_cyan"   )
    table.add_column("Mean time"    , style="magenta"       )
    table.add_column("Median time"  , style="magenta"       )
    table.add_column("Min time"     , style="green"         )
    table.add_column("Max time"     , style="green"         )
    table.add_column("Total time"   , style="bright_red"    )
    table.add_column("Total queries", style="red"           )
    table.add_row(str(q_time['elapsed']          ),
                  str(result['prompt_eval_count']),
                  str(result['eval_count']       ),
                  str(q_time['mean']             ),
                  str(q_time['median']           ),
                  str(q_time['min']              ),
                  str(q_time['max']              ),
                  str(q_time['total']            ),
                  str(q_time['count']            ))
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
          "options": {
            "temperature": self._options['temperature'],
            "top_p": self._options['top_p']
          }
        },
        timeout=self._timeout
      )
      response.raise_for_status()
      self._timer.stop()
      result = response.json()
      self.printStat(result)
      # result.pop('context', None)
      # if options.get("debug", False):
      #   rprint(result)
      return result.get("response", "")
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
      raise Exception(f"Ollama query error: {str(e)}")

# ollama = COllama()
