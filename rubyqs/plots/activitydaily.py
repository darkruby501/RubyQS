# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 16:59:46 2016

@author: RMB
"""


from plots.plots import *

def activitydaily_plotly(offline=False):
    daily_vigor = query("""
        SELECT date(datetime(date_iso,PRINTF('%.0d',substr(tz_offset,1))||' hours')) 
        AS local_time,COUNT(*) AS vigorous_minutes
        FROM biosignals
        WHERE heartrate > 135 AND steps > 60
        GROUP BY local_time""",
                        Basis._DB_PATH,parse_dates=['local_time'],index_col='local_time')
    daily_bio = query("""
        SELECT date(datetime(date_iso,PRINTF('%.0d',substr(tz_offset,1))||' hours')) 
        AS local_time,
            SUM(steps) AS steps,
            SUM(calories) AS calories,
            AVG(heartrate) AS heartrate
        FROM biosignals
        GROUP BY local_time""",
                        Basis._DB_PATH,parse_dates=['local_time'],index_col='local_time')
    
    df = pd.merge(daily_bio,daily_vigor,left_index=True,
                  right_index=True,how='outer').fillna(0).round()
    
    
    trace1 = go.Bar(
        x=df.index,
        y=df['vigorous_minutes'],
        name='Vigorous Activity',
        marker={'color':colors['vigor']},
        yaxis='y3',
        opacity=1
        )
    
    trace2 = go.Bar(
        x=df.index,
        y=df['steps'],
        name='Steps',
        marker={'color':colors['steps']},
        yaxis='y2',
        opacity=1
        )
    
    trace3 = go.Bar(
        x=df.index,
        y=df['calories'],
        name='Calories Burned',
        marker={'color':colors['calories']},
        opacity=0.9
        )
    
    tline1 = go.Scatter(x=xrange(df),y=[15]*2,#name='target waketime',
                line=dict(color=colors['vigor'],width=1.5,dash='dash'),mode='lines',yaxis='y3')
    
    data = [trace1,trace2,trace3,tline1]
    
    layout = go.Layout(
        title='Exercise and Activity',
        barmode='group',
        width=1000,
        margin=dict(t=60,b=60,l=10,r=10,pad=5,autoexpand=True),
        showlegend=False,
        xaxis=dict(showgrid=True,tickformat='%m-%d',hoverformat='%b-%d',tickmode="linear",dtick=86400000*1,
            domain=[0.25, 0.75],autorange=False,range=lastNrange(df,N,True)
            ),
        yaxis=dict(
            title='Calories',
            titlefont=dict(
                color=colors['calories']
            ),
            tickfont=dict(
                color=colors['calories']
            ),
            range=[0,3500],
            side='right',
            position=0.83,
            fixedrange=True
        ),
        yaxis2=dict(
            title='Steps',
            titlefont=dict(
                color=colors['steps']
            ),
            tickfont=dict(
                color=colors['steps']
            ),
            anchor='x',
            overlaying='y',
            side='right',
            fixedrange=True
        ),
        yaxis3=dict(
            title='Vigorous Activity (minutes)',
            titlefont=dict(
                color=colors['vigor']
            ),
            tickfont=dict(
                color=colors['vigor']
            ),
            anchor='left',
            overlaying='y',
            side='left',
            #position=0.15,
            range=[0,45],
            fixedrange=True
        )
    )
    
    
    fig = go.Figure(data=data, layout=layout)
    
    if offline:
        from plotly.offline import init_notebook_mode,plot
        init_notebook_mode()
        plot(fig)
    else:
        py.iplot(fig, filename='QS/activity-daily')
    
if __name__=='__main__':
    activitydaily_plotly()