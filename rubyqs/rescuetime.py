# -*- coding: utf-8 -*-

# Turn into class later

import re
import sqlite3
from datetime import timedelta, date
from hashlib import md5
from io import StringIO

import numpy as np
import pandas as pd
import requests

from rubyqs.utils import query, extract_time

_DB_PATH = r"C:\Users\RMB\Drive\Tsuyoku\QS Data\QuantifedSelf" \
           r"\RubyQS.db"  # SHOULD REALLY GO IN SOME CONFIG FILE


class RescueTime():
    _DB_PATH = '/Users/rbloom/git-personal/rubyqs/rubyqs.db'  # SHOULD REALLY GO IN SOME CONFIG FILE
    _URL_API = 'https://www.rescuetime.com/anapi/data'
    _KEY = 'B63EEMx8wEH8uqz6BTIiPxDmE3V6NJAji1uF4vHt'  # should go in keyring

    def __init__(self, start_date=None, end_date=None, store=False, store_raw=False):
        self.start_date = start_date
        self.end_date = end_date
        self.store = store

    # %% PUBLIC METHODS


    def get_rescuetime_log(self, start_date=None, end_date=None, store=None):
        # If dates not supplied to method, use instance dates
        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date
        if store is None:
            store = self.store

        # If no dates, use last to present
        if start_date is None:
            start_date = self._query_one("SELECT MAX(localdate) FROM rescuetime")[0]
            start_date = start_date[0:10]
        if end_date is None:
            end_date = str(date.today())

        df = self._download_days(start_date, end_date)
        if store:
            self._store_df(df, 'rescuetime')
        return df

    def get_rescuetime_days(self, start_date=None, end_date=None, df=None, ):
        if df is None:  # guid is primary key and fastest to sort
            df = query("""SELECT * FROM
                            rescuetime
                            ORDER BY guid DESC
                            LIMIT 100000
                            """,
                       self._DB_PATH, parse_dates=['localdate'], index_col='localdate')  ###temp!!!
            df = df[end_date:start_date]

        ProdHours = self._log2ProdHours(df)
        WorkTimes = self._log2WorkTimes(df)
        Usages = self._log2Usages(df)

        RescuetimeDays = ProdHours.merge(WorkTimes, left_index=True, right_index=True, how='outer')
        RescuetimeDays = RescuetimeDays.merge(Usages, left_index=True, right_index=True, how='outer')

        return RescuetimeDays

    # %% PRIVATE METHODS
    def _rtlog_preprocess(self, df):
        """Takes in rescuetime_log dataframe and prepares for insertion into table"""
        if 'Number of People' in df.columns:
            df.drop('Number of People', axis=1, inplace=True)
        df.rename(columns={'Time Spent (seconds)': 'seconds', 'Date': 'localdate'},
                  inplace=True)
        df.columns = [col.lower() for col in df.columns]
        rowstring = df.applymap(str).apply(lambda x: ''.join(x), axis=1)
        df['guid'] = rowstring.apply(lambda x: re.sub(r'\W+', '', x[0:16]) +
                                               md5(x.encode()).hexdigest())
        return df

    def _detect_mobile(self, x):
        mobile_keywords = ['android', 'mobile']
        return int(any([y in x['Activity'].lower() or
                        y in x['Document'].lower() for y in mobile_keywords]))

    def _download_days(self, Start_Date, End_Date, Type='Document'):
        date_sequence = pd.date_range(Start_Date, End_Date, freq='D').values
        date_sequence = pd.Series(date_sequence).apply(lambda x: str(x.date())).values

        if len(date_sequence) < 2:
            data = self._download_day([date_sequence[0], date_sequence[0]])
        else:
            dataframes = []
            for i in range(0, len(date_sequence) - 1):
                data = self._download_day([date_sequence[i], date_sequence[i + 1]])
                dataframes.append(data)
                # print('Downloaded:',date_sequence[i])
                data = pd.concat(dataframes)

        data['Document'] = data['Document'].apply(lambda x: (x[0:255]))
        # Create mobile column
        data['mobile'] = data[['Activity', 'Document']].apply(lambda x:
                                                              self._detect_mobile(x), axis=1)
        data = self._rtlog_preprocess(data)  # Create unique id

        return data

    def _download_day(self, daterange, type_='document'):
        Format = 'csv'  # no idea why I'd ever use json

        if (type_ == 'document'):
            params_api = {
                'perspective': 'interval',
                'restrict_kind': 'document',
                'interval': 'interval',
                'resolution_time': 'minute'
            }

        params_api['restrict_begin'] = daterange[0]
        params_api['restrict_end'] = daterange[-1]
        params_api['key'] = self._KEY
        params_api['format'] = Format

        resp = requests.get(self._URL_API, params_api)
        #        print('Status Code: ', resp.status_code) ### Need proper error handling here.
        data = pd.read_csv(StringIO(resp.content.decode()), parse_dates=['Date'])  # ,index_col='Date')
        return data

    def _store_df(self, df, table):
        try:
            db = sqlite3.connect(self._DB_PATH)
            df.to_sql('temp_table', db, if_exists='replace', index=False)
            cursor = db.cursor()
            cursor.execute("""INSERT OR REPLACE INTO {}
                SELECT * FROM temp_table""".format(table))  # yes, not clean, but only used internally
            cursor.execute('DROP TABLE temp_table')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def _query_one(self, query):
        try:
            db = sqlite3.connect(self._DB_PATH)
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        return result

    # Classes for processing RT logs #


    def _log2ProdHours(self, df):
        ProdHours = df.groupby(np.sign(df['productivity']))
        ProdHours = ProdHours.resample('D', how=sum).unstack(level=0)['seconds'] / 3600
        ProdHours['Total_Hours'] = ProdHours.sum(axis=1)
        ProdHours.rename(columns={0: 'Neutral', 1: 'Productive',
                                  -1: 'Unproductive'}, inplace=True)
        return ProdHours

    def _resample5(self, df):
        df = df.resample('5T').sum()
        df = df[df.resample('5T').sum()['seconds'] > 90]
        df = pd.DataFrame(df)
        df['date_shifted'] = df.index
        return df

    def _log2Usages(self, df):
        df['date_shifted'] = (pd.Series(df.index)).apply(lambda x: x + timedelta(hours=-5)).values
        df = df.reset_index()
        df.set_index('date_shifted', inplace=True)

        Usages = {}
        Usages['FirstMobile'] = self._resample5(df[df['mobile'] == True]).resample('D').min()['date_shifted']
        Usages['LastMobile'] = self._resample5(df[df['mobile'] == True]).resample('D').max()['date_shifted']
        Usages['FirstLaptop'] = self._resample5(df[df['mobile'] == False]).resample('D').min()['date_shifted']
        Usages['LastLaptop'] = self._resample5(df[df['mobile'] == False]).resample('D').max()['date_shifted']
        Usages['FirstAll'] = self._resample5(df).resample('D').min()['date_shifted']
        Usages['LastAll'] = self._resample5(df).resample('D').max()['date_shifted']
        Usages = pd.DataFrame(Usages).applymap(lambda x: extract_time(x + timedelta(hours=5)))

        return Usages

    def _log2WorkTimes(self, df):

        df = df[(df['mobile'] == False) & (df['productivity'] == 2)]
        df = df.resample('60T', how='sum')
        df = df[df['seconds'] > 20 * 60]

        df['date_shifted'] = (pd.Series(df.index)).apply(lambda x: x + timedelta(hours=-5)).values
        df = df.reset_index()
        df.set_index('date_shifted', inplace=True)

        dfstart = df.resample('D').min()['localdate'].apply(lambda x: extract_time(x))
        dfstop = df.resample('D').max()['localdate'].apply(lambda x: extract_time(x))

        WorkTimes = pd.DataFrame(data={'FirstWork': dfstart, 'LastWork': dfstop})
        return WorkTimes
