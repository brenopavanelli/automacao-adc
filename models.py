from dataclasses import dataclass
from src.utils import today_formatted_date

@dataclass()
class Employee:
    name: str
    id: int
    role: str
    occupational_group: str

@dataclass()
class Process:
    number: str
    fis: str
    date_of_deferral: str
    section: str

@dataclass()
class DocumentContext:
    employee: Employee
    process: Process
    competence: str
    today: str

    def __post_init__(self):
        self.today = today_formatted_date()