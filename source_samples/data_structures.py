# data_structures.py

from collections import defaultdict
from typing import Any, Dict, List, TypeVar, Optional

K = TypeVar('K')
V = TypeVar('V')


def deduplicate_list(lst: List[Any]) -> List[Any]:
    return list(dict.fromkeys(lst))

def merge_dicts(a: Dict[K, V], b: Dict[K, V]) -> Dict[K, V]:
    return {**a, **b}

def invert_dict(d: Dict[K, V]) -> Dict[V, K]:
    if len(set(d.values())) < len(d.values()):
        raise ValueError("Cannot invert dict with duplicate values.")
    return {v: k for k, v in d.items()}

def group_by_key(items: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict]]:
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get(key)].append(item)
    return dict(grouped)

def nested_get(d: Dict, keys: List[str], default: Optional[Any] = None) -> Any:
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d
