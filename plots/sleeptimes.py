# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 16:57:44 2016

@author: RMB
"""
from plots.plots import *

def sleeptimes_plotly(offline=False):
    SleepDays = Basis().get_sleep_days()['SleepDays']
    df = SleepDays[['bed_time','wake_time']]
    
    df = df.applymap(lambda x: time2fraction(x))
    df = pd.DataFrame({'wake_time':df['wake_time'].shift(1,freq='D'),
                       'bed_time':df['bed_time']})
    df = df.round(1)
    
    trace1 = go.Bar(
                x=df.index,
                y=df['bed_time'],
                name='Bed Time',
                marker={'color':"#003153"})
    trace2 = go.Bar(
                x=df.index,
                y=df['wake_time'],
                name='Wake Time',
                marker={'color':"#FF9933"})
    
    fig = plotly.tools.make_subplots(rows=2, cols=1,
                              subplot_titles=('Bed Time','Wake Time'),
                              vertical_spacing = 0.2
                             )
    
    target_wake = 7.5
    target_bed = 23
    
    tline1 = go.Scatter(x=xrange(df),y=[target_bed]*2,name='target bedtime',
                line=dict(color=("red"),width=2,dash='dash'),mode='lines')
    tline2 = go.Scatter(x=xrange(df),y=[target_wake]*2,name='target waketime',
                line=dict(color=("rgb(0, 0, 0)"),width=2,dash='dash'),mode='lines')
    
    
    
    fig.append_trace(tline2, 2, 1)
    fig.append_trace(tline1, 1, 1)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace1, 1, 1)
    
    fig['layout'].update(
        barmode='stack',
        height=600, 
        width=600,
#        xaxis=dict(showgrid=True,tickformat='%m-%d',hoverformat='%b-%d',
#                   autorange=False,range=lastNrange(df,N,True),
#                   tickmode="linear",dtick=86400000*1),
    #    title='Sleep Times',
        margin=dict(t=60,b=60,l=60,r=50,pad=5,autoexpand=True),
        yaxis1=dict(range=[26,21],fixedrange=True),
        yaxis2=dict(range=[6,11],fixedrange=True)
        )
    
    for axis in ['1','2']:
        fig['layout']['xaxis'+axis].update(showgrid=True,
                                  tickformat='%m-%d',
                                  hoverformat='%b-%d',
                                   tickmode="linear",
                                   dtick=86400000,
                                   autorange=False,
                                   range=lastNrange(df,N,True)
                                  )
        fig['layout']['yaxis'+axis].update(tickmode="linear",
                                           dtick=1,
                                           autorange=False,
                                           tickformat='.2f',
                                           hoverformat='.1f',
                                           fixedrange=True
                                          )
    
    if offline:
        from plotly.offline import init_notebook_mode,plot
        init_notebook_mode()
        plot(fig)
    else:
        py.iplot(fig, filename='QS/sleep-times')
    
if __name__=='__main__':
    sleeptimes_plotly(offline=True)