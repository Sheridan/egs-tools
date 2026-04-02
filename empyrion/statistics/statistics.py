from rich.console import Console
from rich.markup import escape
from rich.table import Table

from empyrion.jsonstorage import CJsonStorage
from empyrion.statistics.history import CHistory

class CStatistics(CJsonStorage):
  def __init__(self):
    super().__init__('trash/statistics.json')

  def appendLLMQueryMetrics(self, llm_model, elapsed_time, in_tokens, out_tokens):
    self._add('llm', llm_model, 'query_elapsed_time', elapsed_time)
    self._add('llm', llm_model, 'query_tokens_in'   , in_tokens)
    self._add('llm', llm_model, 'query_tokens_out'  , out_tokens)

  def _formatSeconds(self, seconds: float) -> str:
    total_seconds = int(round(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

  def showLLM(self):
    llm = self._tool('llm')
    if llm is None:
      return
    history = { }
    total = { 'elapsed_time': CHistory(),
              'tokens_in':    CHistory(),
              'tokens_out':   CHistory() }
    for model in llm:
      if 'query_elapsed_time' in llm[model] and 'query_tokens_in' in llm[model] and 'query_tokens_out' in llm[model]:
        if model not in history:
          history[model] = { 'elapsed_time': CHistory(),
                             'tokens_in':    CHistory(),
                             'tokens_out':   CHistory() }
        history[model]['elapsed_time'].append(llm[model]['query_elapsed_time'])
        history[model]['tokens_in']   .append(llm[model]['query_tokens_in'])
        history[model]['tokens_out']  .append(llm[model]['query_tokens_out'])
        total['elapsed_time'].append(llm[model]['query_elapsed_time'])
        total['tokens_in']   .append(llm[model]['query_tokens_in'])
        total['tokens_out']  .append(llm[model]['query_tokens_out'])


    table = Table(title="LLM statistics", expand=True)
    table.add_column("Model"           , style="cyan")
    table.add_column("Queries"         , style="bright_magenta")
    table.add_column("Query\nmean"      , style="dark_cyan")
    table.add_column("Query\nmedian"    , style="light_sea_green")
    table.add_column("Query\nmax"       , style="deep_sky_blue2")
    table.add_column("Query\nmin"       , style="deep_sky_blue1")
    table.add_column("Query\ntotal"     , style="aquamarine3")
    table.add_column("Tokens\nin"       , style="yellow2")
    table.add_column("Tokens\nin\nmin"   , style="dark_sea_green1")
    table.add_column("Tokens\nin\nmean"  , style="honeydew2")
    table.add_column("Tokens\nin\nmax"   , style="light_cyan1")
    table.add_column("Tokens\nout"      , style="dark_olive_green1")
    for model in history:
      table.add_row(escape(model),
                    str(history[model]['elapsed_time'].count()),
                    escape(self._formatSeconds(history[model]['elapsed_time'].mean())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].median())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].max())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].min())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].sum())),
                    str(int(history[model]['tokens_in'   ].sum())),
                    str(int(history[model]['tokens_in'   ].min())),
                    str(int(history[model]['tokens_in'   ].mean())),
                    str(int(history[model]['tokens_in'   ].max())),
                    str(int(history[model]['tokens_out'  ].sum())))
    table.add_row('Total',
                    str(total['elapsed_time'].count()),
                    escape(self._formatSeconds(total['elapsed_time'].mean())),
                    escape(self._formatSeconds(total['elapsed_time'].median())),
                    escape(self._formatSeconds(total['elapsed_time'].max())),
                    escape(self._formatSeconds(total['elapsed_time'].min())),
                    escape(self._formatSeconds(total['elapsed_time'].sum())),
                    str(int(total['tokens_in'].sum())),
                    str(int(total['tokens_in'].min())),
                    str(int(total['tokens_in'].mean())),
                    str(int(total['tokens_in'].max())),
                    str(int(total['tokens_out'].sum())))
    Console().print(table)

statistics = CStatistics()
