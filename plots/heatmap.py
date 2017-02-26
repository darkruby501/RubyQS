# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:01:30 2016

@author: RMB
"""

from plots.plots import *

def heatmap_plotly():
    df = query("""
        SELECT start_time_iso, end_time_iso, minutes AS duration, type, sleepblock_id,start_time_time_zone_offset
        FROM sleep_stages
        """,
                        Basis._DB_PATH,parse_dates=['start_time_iso','end_time_iso'])
    
    df.tail()
    
    df['start_time_local_time'] = tz_shift(df,'start_time_iso','start_time_time_zone_offset')
    df['end_time_local_time'] = tz_shift(df,'end_time_iso','start_time_time_zone_offset')
    
    stages_ts = pd.Series(index=pd.date_range(df.iloc[0]['start_time_local_time'],df.iloc[-1]['end_time_local_time'],freq='T'))
    
    for stage in df.iterrows():
        stages_ts[stage[1]['start_time_local_time']:stage[1]['end_time_local_time']] = stage[1]['type']
    
    #stages_ts.fillna('awake',inplace=True)
    stages_ts.replace('interruption',np.nan,inplace=True)
    stages_ts.head(20)
    
    slp = pd.get_dummies(stages_ts)
    slp = slp.resample('30T',how='sum')
    Slp = slp.sum(axis=1) > 15
    Slp.replace({True:'asleep',False:np.nan},inplace=True)
    
    
    # Get Time Series of Productivity Status
    
    def rt_act(x):
        if x['total'] < 10:
            return np.nan
        else:
            a = x[0:-1].argmax()
            if x[a] > 15:
                return a
            else: return np.nan
    
    
    df = query("""
        SELECT localdate, productivity, seconds
        FROM rescuetime_log
        WHERE mobile=0
        """,
                        Basis._DB_PATH,parse_dates=['localdate'],index_col=['localdate'])
    
    df = df[df['seconds']<320]
    
    df.reset_index(inplace=True)
    df['productivity'] = np.sign(df['productivity'])
    act = (df.groupby(['productivity','localdate']).sum().unstack(level=0).resample('30T',how='sum')['seconds']/60)
    act['total'] = act.sum(axis=1)
    act.tail(20)
    
    Act = act.apply(rt_act,axis=1).replace({1:'productive',0:'neutral',-1:'unproductive'})        
    Act.tail(20)
    
    # Combine into single series
    
    ALL = Act
    ALL[Slp[Slp.notnull()].index]='asleep'
    
    
    # Create grid for heatmap
    GRID = pd.DataFrame(data={'activity':ALL.values},
                        index=[ALL.index.date,ALL.index.time])
    
    GRID = GRID.unstack(level=1)['activity']
    GRID.columns = [str(col)[0:-3] for col in GRID.columns] #shorten and convert to string
    GRID = lastNdays(GRID,28) #Use only last four weeks
    
    #GRID.index = pd.Series(GRID.index).astype(str).apply(lambda x: x[5:])
    
    #k=14
    #GRID = GRID[GRID.columns[k:].tolist()+GRID.columns[0:k].tolist()] #reorder columns
    #GRID[GRID.columns[0:k].tolist()] = GRID[GRID.columns[0:k].tolist()].shift(-1)
    
    label_map = {np.nan:0,'asleep':0.2,'unproductive':0.4,'neutral':0.6,'productive':1}
    GRID.replace(label_map,inplace=True)
    GRID.sort_index(ascending=False,inplace=True)
    
    
    # Create plot
    
    colorscale = [
        [0.0, colors['intrpt2']],
        [0.2, colors['deep']],
        [0.4, colors['vunprod']],
        [0.6, colors['neutral']],
        [1, colors['vprod']]
    ]
    
    data = [
        go.Heatmap(
        z=GRID.values.tolist(),
       x=GRID.columns.tolist(),
       y=GRID.index.tolist(),
        colorscale=colorscale,
        showscale=False,
    #        showlegend=True
        )
    ]
    
    layout = go.Layout(
        title="Daily Patterns",
        height=400,
        showlegend=False,
        margin=dict(t=80),
        xaxis1=go.XAxis(
            fixedrange=True,
            autorange=True,
            type='category',
            ),
        yaxis=go.YAxis(
            fixedrange=True,
            type='date',
            tickmode="linear",
            dtick=86400000*1,
            tickformat='%m-%d',
            hoverformat='%b-%d'
            )
    )
    
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='QS/heatmap')
    #plotly.offline.iplot(data) 

if __name__=='__main__':
    heatmap_plotly()