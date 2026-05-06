"""
Главный модуль приложения "TimeTracker: Система учета рабочего времени".

Назначение: предоставление графического интерфейса для ввода, редактирования,
сохранения, загрузки, морфологического анализа данных и формирования отчетов.

Автор: студент гр. ИСТ-XXX
Дата: май 2026
Версия: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List

from models import WorkRecord
from file_manager import save_to_csv, load_from_csv, save_dictionary
from morphology import build_frequency_dictionary


class TimeTrackerApp:
    """
    Главный класс приложения. Создает окно, элементы управления,
    обрабатывает события пользователя.
    """

    def __init__(self, root: tk.Tk):
        """
        Инициализация приложения.

        Аргументы:
            root: корневое окно Tkinter
        """
        self.root = root
        self.root.title("TimeTracker - Система учета рабочего времени")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        # Основной список записей
        self.records: List[WorkRecord] = []
        self.next_id = 1

        # Создание интерфейса
        self._create_menu()
        self._create_input_frame()
        self._create_buttons_frame()
        self._create_table_frame()
        self._create_status_bar()

    # ======================== МЕНЮ ========================

    def _create_menu(self):
        """Создать главное меню приложения."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить из файла", command=self.load_from_file)
        file_menu.add_command(label="Сохранить в файл", command=self.save_to_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Отчеты"
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=reports_menu)
        reports_menu.add_command(label="Показать отчет по сотрудникам", command=self.show_report)
        reports_menu.add_command(label="Частотный словарь", command=self.analyze_text)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    # ======================== ПАНЕЛЬ ВВОДА ========================

    def _create_input_frame(self):
        """Создать панель с полями ввода данных."""
        input_frame = ttk.LabelFrame(self.root, text="Ввод данных", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Первая строка: ФИО и Дата
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="ФИО сотрудника:", width=20).pack(side=tk.LEFT, padx=5)
        self.entry_fio = ttk.Entry(row1, width=35)
        self.entry_fio.pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="Дата:", width=10).pack(side=tk.LEFT, padx=5)
        self.entry_date = ttk.Entry(row1, width=15)
        self.entry_date.pack(side=tk.LEFT, padx=5)
        # Подсказка по формату даты
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        ttk.Label(row1, text="ДД.ММ.ГГГГ", foreground="gray").pack(side=tk.LEFT)

        # Вторая строка: Часы и Проект
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="Часы:", width=20).pack(side=tk.LEFT, padx=5)
        self.entry_hours = ttk.Entry(row2, width=10)
        self.entry_hours.pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="Проект:", width=10).pack(side=tk.LEFT, padx=5)
        self.combo_project = ttk.Combobox(row2, width=25, state="readonly")
        self.combo_project['values'] = ("Проект А", "Проект Б", "Проект В", "Общее")
        self.combo_project.current(0)
        self.combo_project.pack(side=tk.LEFT, padx=5)

        # Третья строка: Описание
        row3 = ttk.Frame(input_frame)
        row3.pack(fill=tk.X, pady=2)

        ttk.Label(row3, text="Описание:", width=20).pack(side=tk.LEFT, padx=5, anchor=tk.N)
        self.text_description = tk.Text(row3, width=60, height=3)
        self.text_description.pack(side=tk.LEFT, padx=5)

    # ======================== КНОПКИ ========================

    def _create_buttons_frame(self):
        """Создать панель с кнопками управления."""
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill=tk.X, padx=10)

        ttk.Button(btn_frame, text="Добавить", command=self.add_record).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Сохранить в файл", command=self.save_to_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Загрузить из файла", command=self.load_from_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Анализ текста", command=self.analyze_text).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Отчет", command=self.show_report).pack(side=tk.LEFT, padx=3)

    # ======================== ТАБЛИЦА (Treeview) ========================

    def _create_table_frame(self):
        """Создать таблицу для отображения записей."""
        table_frame = ttk.Frame(self.root, padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Заголовки столбцов
        columns = WorkRecord.get_headers()
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Полосы прокрутки
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещение
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Настройка столбцов
        widths = [50, 200, 100, 80, 150, 250]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_column(c))
            self.tree.column(col, width=width, anchor=tk.CENTER)

        # Привязка двойного клика для редактирования
        self.tree.bind("<Double-1>", self._on_double_click)

    # ======================== СТРОКА СОСТОЯНИЯ ========================

    def _create_status_bar(self):
        """Создать строку состояния."""
        self.status_var = tk.StringVar()
        self.status_var.set("Готово. Записей: 0")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ======================== ЛОГИКА ========================

    def add_record(self):
        """Добавить новую запись в список и таблицу."""
        # Получение данных из полей
        fio = self.entry_fio.get().strip()
        if not fio:
            messagebox.showwarning("Ошибка", "Введите ФИО сотрудника!")
            return

        # Парсинг даты
        date_str = self.entry_date.get().strip()
        try:
            date = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return

        # Парсинг часов
        hours_str = self.entry_hours.get().strip()
        try:
            hours = float(hours_str)
            if hours < 0:
                hours = 0
        except ValueError:
            hours = 0

        project = self.combo_project.get()
        description = self.text_description.get("1.0", tk.END).strip()

        # Создание записи
        record = WorkRecord(
            id=self.next_id,
            employee_name=fio,
            date=date,
            hours=hours,
            project=project,
            description=description
        )
        self.next_id += 1
        self.records.append(record)

        # Добавление в таблицу
        self.tree.insert("", tk.END, iid=str(record.id), values=record.to_list())

        # Очистка полей
        self._clear_inputs()

        # Обновление статуса
        self._update_status()

        # Автопрокрутка к последней записи
        self.tree.see(str(record.id))

    def delete_record(self):
        """Удалить выделенную запись."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления!")
            return

        for item in selected:
            rec_id = int(item)
            # Удаляем из таблицы
            self.tree.delete(item)
            # Удаляем из списка
            self.records = [r for r in self.records if r.id != rec_id]

        self._update_status()

    def save_to_file(self):
        """Сохранить записи в CSV-файл."""
        if not self.records:
            messagebox.showwarning("Ошибка", "Нет данных для сохранения!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="records.csv"
        )
        if filepath:
            save_to_csv(self.records, filepath)
            messagebox.showinfo("Информация", f"Файл сохранен!\n{filepath}")

    def load_from_file(self):
        """Загрузить записи из CSV-файла."""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            try:
                self.records = load_from_csv(filepath)
                self.next_id = max(r.id for r in self.records) + 1 if self.records else 1

                # Очистка и заполнение таблицы
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for rec in self.records:
                    self.tree.insert("", tk.END, iid=str(rec.id), values=rec.to_list())

                self._update_status()
                messagebox.showinfo("Информация", f"Загружено записей: {len(self.records)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл!\n{e}")

    def analyze_text(self):
        """Выполнить морфологический анализ и сохранить частотный словарь."""
        if not self.records:
            messagebox.showwarning("Ошибка", "Нет данных для анализа!")
            return

        # Построение словаря
        freq_dict = build_frequency_dictionary(self.records)

        if not freq_dict:
            messagebox.showinfo("Информация", "Нет слов для анализа в описаниях.")
            return

        # Сохранение
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="dictionary.csv"
        )
        if filepath:
            save_dictionary(freq_dict, filepath)
            messagebox.showinfo("Информация", f"Словарь сохранен!\nСлов: {len(freq_dict)}")

    def show_report(self):
        """Показать отчет по сотрудникам."""
        if not self.records:
            messagebox.showwarning("Ошибка", "Нет данных для формирования отчета!")
            return

        # Группировка по сотрудникам
        report_lines = ["ОТЧЕТ ПО СОТРУДНИКАМ:", ""]
        employee_data = {}

        for rec in self.records:
            if rec.employee_name not in employee_data:
                employee_data[rec.employee_name] = {"total_hours": 0, "count": 0}
            employee_data[rec.employee_name]["total_hours"] += rec.hours
            employee_data[rec.employee_name]["count"] += 1

        for name, data in employee_data.items():
            report_lines.append(f"{name}: {data['total_hours']} часов, записей: {data['count']}")

        report_text = "\n".join(report_lines)
        messagebox.showinfo("Отчет", report_text)

    def show_about(self):
        """Показать окно 'О программе'."""
        messagebox.showinfo(
            "О программе",
            "TimeTracker v1.0\n"
            "Система учета рабочего времени\n\n"
            "Разработано в рамках контрольной работы\n"
            "по дисциплине ТППОИС, 2026 г.\n\n"
            "Назначение: автоматизация учета рабочего\n"
            "времени сотрудников предприятия.\n\n"
            "Python + Tkinter"
        )

    def _clear_inputs(self):
        """Очистить поля ввода."""
        self.entry_fio.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.entry_hours.delete(0, tk.END)
        self.combo_project.current(0)
        self.text_description.delete("1.0", tk.END)

    def _update_status(self):
        """Обновить строку состояния."""
        total_hours = sum(r.hours for r in self.records)
        self.status_var.set(
            f"Записей: {len(self.records)} | "
            f"Всего часов: {total_hours:.1f} | "
            f"Сотрудников: {len(set(r.employee_name for r in self.records))}"
        )

    def _sort_column(self, col: str):
        """Сортировка таблицы по столбцу при клике на заголовок."""
        # Получаем индекс столбца
        headers = WorkRecord.get_headers()
        col_index = headers.index(col)

        # Извлекаем данные
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]

        # Пробуем сортировать как числа
        try:
            data.sort(key=lambda x: float(x[0].replace(",", ".")) if x[0] else 0)
        except ValueError:
            data.sort(key=lambda x: x[0])

        # Перемещаем элементы
        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)

    def _on_double_click(self, event):
        """Обработчик двойного клика по строке таблицы."""
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.tree.item(item, "values")

        # Заполняем поля ввода данными из выделенной строки
        self.entry_fio.delete(0, tk.END)
        self.entry_fio.insert(0, values[1])

        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, values[2])

        self.entry_hours.delete(0, tk.END)
        self.entry_hours.insert(0, values[3])

        # Проект
        project = values[4]
        if project in self.combo_project['values']:
            self.combo_project.set(project)
        else:
            self.combo_project.current(0)

        self.text_description.delete("1.0", tk.END)
        self.text_description.insert("1.0", values[5])

        # Удаляем старую запись (будет заменена новой при нажатии "Добавить")
        rec_id = int(item)
        self.tree.delete(item)
        self.records = [r for r in self.records if r.id != rec_id]
        self._update_status()


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()