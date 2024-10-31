from typing import Any, Dict, List
import csv
from io import StringIO

def to_csv_stringio(field_names: List[str], data: List[Dict[str, Any]]) -> StringIO:
    sio = StringIO()
    writer = csv.DictWriter(sio, fieldnames=field_names)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return sio
