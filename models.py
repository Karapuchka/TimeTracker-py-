"""
Модель данных для системы учета рабочего времени.

Содержит класс WorkRecord, представляющий одну запись учета времени.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkRecord:
    """
    Запись учета рабочего времени.

    Атрибуты:
        id (int): уникальный идентификатор записи
        employee_name (str): ФИО сотрудника
        date (datetime): дата выполнения работы
        hours (float): количество отработанных часов
        project (str): название проекта
        description (str): текстовое описание выполненной работы
    """
    id: int
    employee_name: str
    date: datetime
    hours: float
    project: str
    description: str

    def to_list(self) -> list:
        """Преобразовать запись в список для отображения в таблице."""
        return [
            self.id,
            self.employee_name,
            self.date.strftime("%d.%m.%Y"),
            self.hours,
            self.project,
            self.description
        ]

    @staticmethod
    def get_headers() -> list:
        """Возвращает заголовки столбцов таблицы."""
        return ["ID", "Сотрудник", "Дата", "Часы", "Проект", "Описание"]