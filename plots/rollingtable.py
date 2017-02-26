# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:23:16 2016

@author: RMB
"""

from plots.plots import *
from plotly.tools import FigureFactory as FF

def rollingtable_plotly(offline=False):
    df = Basis().get_sleep_days()['SleepDays']
    
    wake_on_time =(df['wake_time']>time(7))&(df['wake_time']<time(8,30))
    wake_on_time[df['wake_time'].isnull()]=np.nan
    wake_on_time = wake_on_time.shift(1,freq='D')
    
    bed_on_time =(df['bed_time'].apply(lambda x: time2fraction(x,add24=True)<23))
    bed_on_time[df['bed_time'].isnull()]=np.nan
    
    
    df = RescueTime().get_rescuetime_days()
    daily_prod = df['Productive']
    
    daily_vigor = query("""
        SELECT date(datetime(date_iso,PRINTF('%.0d',substr(tz_offset,1))||' hours')) AS local_time,COUNT(*) AS vigorous_minutes
        FROM biosignals
        WHERE heartrate > 140 AND steps > 60
        GROUP BY local_time""",
                        Basis._DB_PATH,parse_dates=['local_time'],index_col='local_time')
    
    daily_vigor= daily_vigor['vigorous_minutes']
    
    ma = 3
    
    Targets = pd.DataFrame(data={
            'Prod MA(3)': pd.rolling_mean(df['Productive'],ma).round(1),
            'Activity SUM(3)': pd.rolling_sum(daily_vigor.align(daily_prod,axis=0,fill_value=0)[0],ma),
            'Bed on Time':bed_on_time.astype(bool),
            'Wake on Time':wake_on_time.astype(bool)        
            }
    )
    
    Targets['Bed on Time MA(3)'] = pd.rolling_mean(Targets['Bed on Time'],ma).round(2)
    Targets['Wake on Time MA(3)'] = pd.rolling_mean(Targets['Wake on Time'],ma).round(2)
    
    Targets = Targets[['Prod MA(3)','Activity SUM(3)','Wake on Time','Bed on Time',
                       'Wake on Time MA(3)','Bed on Time MA(3)']]
    Targets.sort_index(ascending=False,inplace=True)
    Targets.index = Targets.index.date
    
    table = FF.create_table(Targets.head(7), index=True, index_title='Date')

    if offline:
        from plotly.offline import init_notebook_mode,plot
        init_notebook_mode()
        plot(table)
    else:    
        py.iplot(table, filename='QS/rolling-table')
    #plotly.offline.iplot(table)
    

    
if __name__=='__main__':
    rollingtable_plotly(offline=True)
