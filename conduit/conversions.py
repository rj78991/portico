from datetime import datetime, timedelta
from dateutil.parser import parse
import numpy as np
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows


def time_to_millis_since_epoch(time):
    """
    convert a datetime to milliseconds since epoch

    :param time: a datetime.datetime instance
    :return: number of milliseconds between given time and epoch
    """
    if isinstance(time, str):
        time = parse(time)
    return round((time - datetime.utcfromtimestamp(0)).total_seconds() * 1000)


def millis_since_epoch_to_time(millis):
    """
    convert number of milliseconds since epoch to a datetime

    :param millis: number of elapsed milliseconds since epoch
    :return: datetime.datetime corresponding to millis
    """
    millis = int(millis)
    return datetime.utcfromtimestamp(0) + timedelta(milliseconds=millis)


def millis_since_epoch_to_date(millis):
    """
    convert number of milliseconds since epoch to a date without a time

    :param millis: number of elapsed milliseconds since epoch
    :return: datetime.date corresponding to millis, dropping the time of day
    """
    millis = int(millis)
    return (datetime.utcfromtimestamp(0) + timedelta(milliseconds=millis)).date()


def make_numeric(dataframe):
    """
    coerce dataframe to numeric, leaving any columns that contain non-numeric data

    :param dataframe: input dataframe
    """
    for col in dataframe.columns:
        dataframe[col] = pd.to_numeric(
            dataframe[col].replace('NaN', np.NaN),
            errors='ignore')


def data_frame_to_excel_tab(dataframe, workbook, tab_name, index):
    """
    Write header and content of dataframe to specified tab in the argument workbook
    :param dataframe: data frame to be emitted into workbook
    :param workbook: openpyxl workbook
    :param tab_name: name of worksheet
    :param index: False if index should be omitted
    :return:
    """
    if tab_name in workbook.sheetnames:
        worksheet = workbook[tab_name]
    else:
        worksheet = workbook.create_sheet(tab_name)
    for row in dataframe_to_rows(dataframe, index=index, header=True):
        worksheet.append(row)
