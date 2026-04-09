import sqlite3
import os
from typing import Optional, Union, Tuple, Dict

class CDatabase:
  def __init__(self, db_path: str = ":memory:"):
    self._db_path = db_path
    self._connection: Optional[sqlite3.Connection] = sqlite3.connect(self._db_path)
    self._connection.execute("PRAGMA foreign_keys = ON")
    self._connection.row_factory = sqlite3.Row

  def connection(self):
    return self._connection

  def query(self, sql: str, params: Union[Tuple, Dict, None] = None) -> sqlite3.Cursor:
    try:
      cursor = self._connection.execute(sql, params) if params else self._connection.execute(sql)
      self._connection.commit()
      return cursor
    except Exception as e:
      self._connection.rollback()
      raise RuntimeError(f"Ошибка выполнения SQL-запроса: {e}") from e

  def close(self) -> None:
    if self._connection:
      self._connection.close()
      self._connection = None

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
