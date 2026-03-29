import time
from typing import Dict
import statistics

class Timer:
  def __init__(self):
    self._start_time: float | None = None
    self._history: list[float] = []
    self._last_elapsed: float = 0.0
    self._maximum: float = 0
    self._minimum: float = 99999999.99

  def start(self) -> None:
    self._start_time = time.perf_counter()

  def stop(self) -> float:
    if self._start_time is None:
      raise RuntimeError("Таймер не был запущен (вызовите start перед stop)")

    end_time = time.perf_counter()
    elapsed = end_time - self._start_time

    if elapsed > self._maximum:
      self._maximum = elapsed

    if elapsed < self._minimum:
      self._minimum = elapsed

    self._history.append(elapsed)
    self._last_elapsed = elapsed
    self._start_time = None

    return elapsed

  def _format_seconds(self, seconds: float) -> str:
    total_seconds = int(round(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

  def get(self) -> Dict[str, str]:
    return {
      'elapsed': self._format_seconds(self._last_elapsed),
      'mean': self._format_seconds(statistics.mean(self._history)),
      'median': self._format_seconds(statistics.median(self._history)),
      'max': self._format_seconds(self._maximum),
      'min': self._format_seconds(self._minimum),
      'total': self._format_seconds(sum(self._history)),
      'count': len(self._history)
    }
