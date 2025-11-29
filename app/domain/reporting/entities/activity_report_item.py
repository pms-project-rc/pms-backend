from dataclasses import dataclass

@dataclass
class ActivityReportItem:
    label: str
    count: int
    total_amount: int
