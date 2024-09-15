from typing import Iterable, Protocol

from .column import Column
from .cell_error import CellError


class Model(Protocol):
    """
    Протокол модели данных для табличного редактора
    Должен описывать и возвращаеть столбцы для редактора значения для ячеек,
    уметь добавлять и удалять строки сохранять изменения в хранилище

    Процесс работы редактора с моделью.

      |-1. Первичная загрузка данных и построение таблицы
      |    Редактор запрашивает у модели столбцы и строки и рисует таблицу
      |-+
      | 2. Ожидание операций от пользователя
      | 3. Обновление модели в соответствии с операцией пользователя
      | 4. Полная перерисовка таблицы с данными от измененной модели
      |-+

    Операции пользователя:
    1. Удаление строки

       Методы модели:
        1. delete_row()
        2. get_row_state()

       Отмена операции:
        1. restore_row()

       Редактор получает состояние строки с помощью get_row_state()
       и удаляет строку, в случае отмены операции использует сохраненное состояние и запускает restore_row()

    2. Добавление строки

       Методы модели:
        1. insert_row()

       Отмена операции:
        1. delete_row()

    3. Установка значения

       Методы модели:
        1. set_value_at()

       Отмена операции:
        1. set_value_at() Записывает прошлое значение в ячейку

       ** ВАЖНО **
       Модель должна иметь возможность хранить любые переданые значения
       в стороковом виде даже если они невалидны для этого типа ячейки
       для того чтобы пользователь мог записать любое значение
       Далее вступит в ход валидация ячеек с проверкой значения для типа
       ** **

    4. Запись значения в диапазон

       Методы модели:
        1. set_value_at()

       Отмена операции:
        1. set_value_at() Записывает прошлое значение в ячейку

       последовательное использования set_value_at() для каждой ячейки диапазона

    5. Вставка таблицы из буфера обмена
       Методы модели:
        1. set_value_at()
        + методы операции "добавить строку" (если необходимо)

       Отмена операции:
        1. set_value_at() Записывает прошлое значение в ячейку
        + отмена операции "добавить строку"

       последовательное использование set_value_at() с соответствующим значением
       вставляемой таблицы для каждой ячейки со смещением на выбранную ячейку или начало выбранного диапазона.

       Если ширина таблицы больше чем количество столбцов + смещение курсора
       по горизонтали, то выводится ошибка

       Если высота таблицы больше чем количество строк + смещение курсора
       по вертикали, то добавляется необходимое количество пустых строк

    6. Вставка значения из буфера обмена

       Методы модели:
        1. set_value_at()

       Отмена операции:
        1. set_value_at() Записывает прошлое значение в ячейку

       Тоже самое что и запись значения в диапазон

    7. сохранение

       Методы модели:
        1. save()

       Отмена операции:
        Эту операцию нельзя отменить

       Модель должна обновить хранилище исходя из изменений, накопленых от
       редактора и перевести модель в состояние have_shanges() == False

    8. Перемещение строк (разрабатывается)

    Все остальные операции не затрагивают модель
    """

    def get_columns(self) -> Iterable[Column]:
        """
        Возвращает столбцы для редактора
        """
        raise NotImplementedError("Method get_columns() not implemented.")

    def total_rows(self) -> int:
        """
        Возвращает количество строк для редактора
        """
        raise NotImplementedError("Method total_rows() not implemented.")

    def get_value_at(self, col: int, row: int) -> str:
        """
        Возвращает строковое представление значения
        """
        raise NotImplementedError("Method get_value_at() not implemented.")

    def set_value_at(self, col: int, row: int, value: str):
        """
        Устанавливает значение в ячейку
        """
        ...

    def save(self) -> bool:
        """
        Сохраняте изменения
        """
        return True

    def insert_row(self, row: int):
        """
        Добавляет новую строку
        """
        ...

    def delete_row(self, row: int):
        """
        Удаляет строку
        """
        ...

    def get_row_state(self, row: int):
        """
        Возвращает состояние строки которое можно использовать для ее востановления
        """
        ...

    def restore_row(self, row: int, state):
        """
        Восстанававливает данные строки по ее состоянию
        """
        ...

    def have_changes(self) -> bool:
        """
        Вернет true если модель имеет несохраненные изменения
        """
        return False