from collections import Counter


def list_difference(left, right):
  return list((Counter(left) - Counter(right)).elements())
