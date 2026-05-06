"""
Модуль для работы с файлами.

Содержит функции сохранения и загрузки записей в CSV-формате,
а также сохранения частотного словаря.
"""

import csv
from datetime import datetime
from typing import List, Dict

from models import WorkRecord


def save_to_csv(records: List[WorkRecord], filepath: str) -> None:
    """
    Сохранить список записей учета времени в CSV-файл.

    Аргументы:
        records: список записей WorkRecord
        filepath: путь к файлу для сохранения
    """
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        # Заголовок
        writer.writerow(["ID", "Сотрудник", "Дата", "Часы", "Проект", "Описание"])
        # Данные
        for rec in records:
            writer.writerow([
                rec.id,
                rec.employee_name,
                rec.date.strftime("%d.%m.%Y"),
                rec.hours,
                rec.project,
                rec.description
            ])


def load_from_csv(filepath: str) -> List[WorkRecord]:
    """
    Загрузить список записей учета времени из CSV-файла.

    Аргументы:
        filepath: путь к файлу для загрузки

    Возвращает:
        список записей WorkRecord
    """
    records = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)  # пропускаем заголовок
        for row in reader:
            if len(row) >= 6:
                records.append(WorkRecord(
                    id=int(row[0]),
                    employee_name=row[1],
                    date=datetime.strptime(row[2], "%d.%m.%Y"),
                    hours=float(row[3]),
                    project=row[4],
                    description=row[5]
                ))
    return records


def save_dictionary(dictionary: Dict[str, int], filepath: str) -> None:
    """
    Сохранить частотный словарь в CSV-файл.

    Аргументы:
        dictionary: словарь {слово: частота}
        filepath: путь к файлу для сохранения
    """
    # Сортируем по убыванию частоты
    sorted_dict = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)

    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Слово", "Частота"])
        for word, freq in sorted_dict:
            writer.writerow([word, freq])