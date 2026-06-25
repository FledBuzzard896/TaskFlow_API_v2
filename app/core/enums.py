from enum import Enum

class TaskStatus(str, Enum):
    IN_PROGRESS = "Выполняется"
    IN_PLAN = "Запланирована"
    COMPLETED = "Завершена"
    DROPPED = "Брошена"

class TaskPriority(str, Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"