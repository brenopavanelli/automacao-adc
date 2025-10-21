from dataclasses import dataclass

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
    # today: str





