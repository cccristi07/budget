import os
from os.path import isfile, join
import sys
import pandas as pd
import numpy as np
import datetime
from dateutil.parser import parse
import matplotlib.pyplot as plt
import seaborn as sb


csv_folder = 'csv/'

to_drop = ["Data", "Detalii tranzactie", "Debit", "Credit"]
to_keep = ['Unnamed: 0', 'Unnamed: 2', 'Unnamed: 5', 'Unnamed: 7']

renamed = dict(zip(to_keep, to_drop))

class Bank:

    ING = "ING" # only one that's implemented


class Reports:

    def __init__(self, report_type):
        self.report_type = report_type

    def is_date(date):
        try:
            date = parse(date)
        except ValueError:
            return False

        return date

    def date_converter(date):

        corr_dates = {
            "ianuarie": "jan",
            "februarie": "feb",
            "martie": "mar",
            "aprilie": "apr",
            "mai": "may",
            "iunie": "jun",
            "iulie": "jul",
            "august": "aug",
            "septembrie": "sep",
            "octombrie": "oct",
            "noiembrie": "nov",
            "decembrie": "dec"
        }
        if date == "":
            return False

        toks = date.split()
        if not toks[0].isdigit():
            return False
        toks[1] = corr_dates[toks[1]]

        parsed_date = is_date(" ".join(toks))

        return parsed_date

    # scan all files in the CSV folder
    csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if
                 os.path.isfile(join(csv_folder, f))]

    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        df = df.replace(np.nan, '', regex=True)
        df = df.drop('Unnamed: 4', axis=1)
        df = df.drop(to_drop, axis=1)
        df = df.rename(index=str, columns=renamed)
        dfs.append(df)


    # because the csv bank format is fucking retarded I need to do a workaround in order to get the meaningful data from it
    insights = []
    for df in dfs:
        # select only the indexes where real dates appear

        ind = df[df["Data"] != ''].index.values
        # create a new dataframe
        dates = []
        incomes = []
        expenses = []
        details = []

        for curr, nxt in zip(ind, ind[1:]):
            # check each entry
            entry = df[curr:nxt]
            entry = entry[:-1]


            date = date_converter(entry["Data"][0])
            # skip if entry is not date related
            if date is False:
                continue
            dates.append(date)
            expense = entry["Debit"][0]
            expense = expense.replace(".", "")
            expense = float(expense.replace(",", ".")) if expense is not '' else 0

            income = entry["Credit"][0]
            income = income.replace(".", "")
            income = float(income.replace(',', '.')) if income is not '' else 0


            expenses.append(expense)
            incomes.append(income)
            details.append(" ".join(entry["Detalii tranzactie"]))

        df_dict = {
            "Date": dates,
            "Expenses": expenses,
            "Incomes": incomes,
            "Details": details
        }

        imp_df = pd.DataFrame(data=df_dict)
        insights.append(imp_df)

    # plots that could be useful
    for df in insights:
        dfs = df.groupby('Date').sum()
        dfs["Cumulative Expenses"] = dfs["Expenses"].cumsum(axis=0)
        dfs.plot()
        month = df.Date[0].month
        plt.title("Month {}".format(month))
        plt.savefig("budget_m{}".format(month))

