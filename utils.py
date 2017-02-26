import pandas as pd
import numpy as np
import datetime
import sqlite3

def extract_time(x):
    if pd.notnull(x):
        return x.time() 
    else: return x

def datetime2time(x):
    if pd.notnull(x):
        return x.time() 
    else: return x

def time2fraction(x,add24=True):
    if (pd.notnull(x) and (type(x)==datetime.time or 
            type(x)==datetime.datetime or 
            type(x)==pd.tslib.Timestamp)):
        t = x.hour + x.minute/60
        if add24:
           	if (np.floor(t)<5):
                  t+=24
        return t
    else:
        return x

def time2fraction_str(x,add24=True):
    if (x!='NaT' and pd.notnull(x)):
        x = datetime.datetime.strptime(x,'%H:%M:%S').time()         
        t = x.hour + x.minute/60
        if add24:
           	if (np.floor(t)<5):
                  t+=24
        return t
    else:
        return np.nan

def tz_shift(df,original,shift):
    if type(df.iloc[0][original])==str:
        df[original] = pd.to_datetime(df[original])
    return df[original] + df[shift].apply(
        lambda x: datetime.timedelta(minutes=int(x if abs(x) > 25 else x*60)))
#

def query(query,db_path,**kwargs):
    """Wrapper for database query"""
    try:
        db = sqlite3.connect(db_path)
        df = pd.read_sql(query,db,**kwargs) #parse_dates=['start_time_iso','end_time_iso'])#,
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()         
    return df
    

#%%        
