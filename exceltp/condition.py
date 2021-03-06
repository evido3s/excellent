# -*- coding: utf-8 -*-
import datetime
from abc import abstractmethod
from enum import Enum
from exceltp.define import *


class ColumnType(Enum):
   date = 0
   integer = 1
   string = 2


class MatchResult(Enum):
    match = 0
    no_match = 1
    invalid_row = 2
    invalid_column = 3
    invalid_value = 4


class ConditionGroup:

    def __init__(self, group_name, group_conf):
        self.group_name = group_name
        self.condition_list = []

        if group_conf is not None:
            self._parse_conf(group_conf)

    def _parse_conf(self, group_conf):
        # process 'group_conf' list info
        for condition_dict in group_conf:

            # process dict info(condition)
            for condition_name, condition_conf in condition_dict.items():
                cond = self._create_condition(condition_name, condition_conf)

            if cond is not None:
                self.condition_list.append(cond)

    def _create_condition(self, cond_name, cond_conf):
        if cond_conf[COLUMN_TYPE] == ColumnType.date.name:
            cond = DateCondition(cond_name, cond_conf)
        elif cond_conf[COLUMN_TYPE] == ColumnType.integer.name:
            cond = IntCondition(cond_name, cond_conf)
        elif cond_conf[COLUMN_TYPE] == ColumnType.string.name:
            cond = StringCondition(cond_name, cond_conf)

        return cond

    def count(self):
        return len(self.condition_list)

    def add_condition(self, cond):
        self.condition_list.append(cond)

    def remove_condition(self, cond):
        return self.condition_list.remove(cond)

    def match(self, row):
        # TODO : change search of all cell to condition cell
        # 'AND" logic : the conditions must all be true
        for cell in row:
            for cond in self.condition_list:
                result = cond.match(cell)
                if result == MatchResult.invalid_column:
                    continue

                if result != MatchResult.match:
                    return False

        return True


class Condtion:

    def __init__(self, cond_name, cond_conf):
        self.condition_name = cond_name
        self.column_name = cond_conf[COLUMN_NAME]
        self.column_type = None
        self.row_startline = cond_conf[ROW_STARTLINE]
        self.condition = cond_conf[CONDITION]
        self.value = cond_conf[CONDITION_VALUE]

    def get_column_name(self):
        return self.column_name.upper()

    def get_column_type(self):
        return self.column_type

    def get_row_startline(self):
        return self.row_startline

    @abstractmethod
    def match(self, data):
        pass


class DateCondition(Condtion):

    def __init__(self, cond_name, cond_conf):
        self.column_type = ColumnType.date
        super().__init__(cond_name, cond_conf)

        self.criteria_date = datetime.datetime.now()

    def set_criteria_date(self, date):
        self.criteria_date = date

    def _today_equal(self, data):
        compare_date = self.criteria_date + datetime.timedelta(int(self.value))

        if data.value.year == compare_date.year and \
                data.value.month == compare_date.month and \
                data.value.day == compare_date.day:
            return MatchResult.match
        else:
            return MatchResult.no_match

    def _today_range_in(self, data):
        range_data = self.criteria_date + datetime.timedelta(int(self.value))

        if int(self.value) >= 0:
            if self.criteria_date <= data.value and data.value <= range_data:
                return MatchResult.match

            return MatchResult.no_match
        else:
            if self.criteria_date >= data.value and data.value >= range_data:
                return MatchResult.match

            return MatchResult.no_match

    def _today_range_over(self, data):
        range_data = self.criteria_date + datetime.timedelta(int(self.value))

        if int(self.value) >= 0:
            if data.value > range_data:
                return MatchResult.match

            return MatchResult.no_match
        else:
            if data.value < range_data:
                return MatchResult.match

            return MatchResult.no_match

    def match(self, data):
        """@data: datetime"""
        if self.get_column_name() != str(data.column):
            return MatchResult.invalid_column

        if self.get_row_startline() > data.row:
            return MatchResult.invalid_row

        if not data.is_date:
            return MatchResult.invalid_value

        if self.condition == CONDITION_TODAY_EQUAL:
            return self._today_equal(data)
        elif self.condition == CONDITION_TODAY_RANGE_IN:
            return self._today_range_in(data)
        elif self.condition == CONDITION_TODAY_RANGE_OVER:
            return self._today_range_over(data)

        return MatchResult.no_match


# TODO: integer
class IntCondition(Condtion):
    pass


# TODO: string
class StringCondition(Condtion):
    pass
