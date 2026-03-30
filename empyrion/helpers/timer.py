import ast
import time
from typing import Dict
import statistics

class Timer:
  def __init__(self):
    self._start_time: float | None = None

  def start(self) -> None:
    self._start_time = time.perf_counter()

  def stop(self) -> float:
    if self._start_time is None:
      raise RuntimeError("Таймер не был запущен (вызовите start перед stop)")
    end_time = time.perf_counter()
    elapsed = end_time - self._start_time
    self._start_time = None
    return elapsed
