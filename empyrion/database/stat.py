from empyrion.database.database import CDatabase
from rich.console import Console
from rich.markup import escape
from rich.table import Table

database = CDatabase("trash/stat.db")

class CStatDB:
  def __init__(self):
    self._stat_f = ['min', 'avg', 'max', 'sum']
    self._create()

  def _create(self) -> None:
    database.query("""
        create table if not exists llm_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            llm_model             text,
            prompt_len            int,
            answer_len            int,
            thinking_len          int,
            load_duration         int,
            prompt_eval_duration  int,
            eval_duration         int,
            total_duration        int,
            prompt_eval_count     int,
            eval_count            int)
    """)

  def append(self, prompt_len, query_result):
    database.query( """
                    insert into llm_stats
                    (
                      llm_model,
                      prompt_len,
                      answer_len,
                      thinking_len,
                      load_duration,
                      prompt_eval_duration,
                      eval_duration,
                      total_duration,
                      prompt_eval_count,
                      eval_count
                    ) values (?,?,?,?,?,?,?,?,?,?)
                    """,
                      (
                        query_result['model'],
                        prompt_len,
                        len(query_result['response'])        if 'response'             in query_result else None,
                        len(query_result['thinking'])        if 'thinking'             in query_result else None,
                        query_result['load_duration']        if 'load_duration'        in query_result else None,
                        query_result['prompt_eval_duration'] if 'prompt_eval_duration' in query_result else None,
                        query_result['eval_duration']        if 'eval_duration'        in query_result else None,
                        query_result['total_duration']       if 'total_duration'       in query_result else None,
                        query_result['prompt_eval_count']    if 'prompt_eval_count'    in query_result else None,
                        query_result['eval_count']           if 'eval_count'           in query_result else None,
                      )
                    )

  def _queryField(self, name):
    result = []
    for f in self._stat_f:
      result.append(f'{f}({name}) as {f}_{name}')
    return ','.join(result)

  def _fmt(self, x):
    if x is None:
      return '-'
    if isinstance(x, int):
      return str(x)
    if isinstance(x, float):
      return f'{x:.2f}'
    return str(x)

  def _fmtNum(self, row, name):
    return tuple(self._fmt(row[f'{f}_{name}']) for f in self._stat_f)

  def _formatNanoseconds(self, nanoseconds: int) -> str:
    nanoseconds = int(nanoseconds)

    total_seconds_int = nanoseconds // 1_000_000_000
    remaining_ns = nanoseconds % 1_000_000_000
    centiseconds = (remaining_ns + 5_000_000) // 10_000_000

    if centiseconds >= 100:
        centiseconds = 0
        total_seconds_int += 1

    hours = total_seconds_int // 3600
    minutes = (total_seconds_int % 3600) // 60
    secs = total_seconds_int % 60

    parts = []
    if hours > 0:
      parts.append(f"{hours}h")
    if minutes > 0:
      parts.append(f"{minutes:02d}m")
    parts.append(f"{secs:02d}.{centiseconds:02d}s")
    return " ".join(parts)

  def _fmtDur(self, row, name):
    return tuple(self._formatNanoseconds(row[f'{f}_{name}']) for f in self._stat_f)

  def show(self):

    for q_part in [['llm_model', 'group by llm_model'], ['"Total" as llm_model', '']]:
      statistics = database.query(f"""
                                  select
                                    {q_part[0]},
                                    count(*) as queries,
                                    {self._queryField('prompt_len')},
                                    {self._queryField('answer_len')},
                                    {self._queryField('thinking_len')},
                                    {self._queryField('load_duration')},
                                    {self._queryField('prompt_eval_duration')},
                                    {self._queryField('eval_duration')},
                                    {self._queryField('total_duration')},
                                    {self._queryField('prompt_eval_count')},
                                    {self._queryField('eval_count')}
                                  from llm_stats {q_part[1]}
                                  """)
      for row in statistics:
        table = Table(title=f"{escape(row['llm_model'])} queries: {row['queries']}", expand=True)
        table.add_column("Type"   , style="cornsilk1")
        table.add_column("Minimum", style="deep_sky_blue1")
        table.add_column("Average", style="cyan3")
        table.add_column("Maximum", style="turquoise2")
        table.add_column("Summ"   , style="slate_blue1")
        table.add_row('Prompt length'      , *self._fmtNum(row, 'prompt_len'))
        table.add_row('Answer length'      , *self._fmtNum(row, 'answer_len'))
        table.add_row('Thinking length'    , *self._fmtNum(row, 'thinking_len'))
        table.add_row('Imput tokens'       , *self._fmtNum(row, 'prompt_eval_count'))
        table.add_row('Output tokens'      , *self._fmtNum(row, 'eval_count'))
        table.add_row('Model loading'      , *self._fmtDur(row, 'load_duration'))
        table.add_row('Prompt evaluating'  , *self._fmtDur(row, 'prompt_eval_duration'))
        table.add_row('Tokens generating'  , *self._fmtDur(row, 'eval_duration'))
        table.add_row('Response generating', *self._fmtDur(row, 'total_duration'))
        Console().print(table)

statistics = CStatDB()
