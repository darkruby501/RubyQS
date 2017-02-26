# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 16:54:55 2016

@author: RMB
"""
from plots.plots import *


def sleepdetailed_plotly(offline=False):
    
    slpclr = ['deep','rem','light','nap','intrpt2']
    
    SleepDays = Basis().get_sleep_days()['SleepDays']
    
    df = (SleepDays[['deep_minutes','rem_minutes','light_minutes',
                     'nap_minutes','interruption_total_minutes']]/60).fillna(0).copy()
    df = df.rename(columns=lambda x: x.replace('_minutes','')).round(1)
    df = df.shift(1,freq='D')
    df.rename(columns={'interruption_total':'interruptions'},inplace=True)     
     
    data = [] #data for plotly plot
    i=0
    for col in df.columns:
        trace = go.Bar(
                x=df.index,
                y=df[col],
                name=col,
                marker={'color':colors[slpclr[i]]}
        )
        data.append(trace)
        i+=1
    
    tline1 = go.Scatter(x=xrange(df),y=[8]*2,name='target hours',showlegend=False,
                line=dict(color=("rgb(0, 0, 0)"),width=2,dash='dot'),mode='lines')
    tline2 = go.Scatter(x=xrange(df),y=[1]*2,showlegend=False,
                line=dict(color=("red"),width=2,dash='dot'),mode='lines')
    
    trace_intrpt = go.Scatter(
            x=df.index,
            y=SleepDays['interruptions'].shift(1,freq='D'),
            name='number of interruptions',
            mode='markers',
            line=dict(color='red',width=3,dash='solid'),marker=dict(size=8),
            opacity=0.8
            )
    
    data.extend([tline1,tline2,trace_intrpt])
    
    layout = go.Layout(
        barmode='stack',
        yaxis=dict(tickformat='.1f',tickmode="linear",dtick=1,fixedrange=True,
                   title='Hours'),
        xaxis=dict(showgrid=True,tickformat='%m-%d',hoverformat='%b-%d',
                   autorange=False,range=lastNrange(df,N,True),
                   tickmode="linear",dtick=86400000*1),
        title='Daily Sleep Duration',
        margin=dict(t=60,b=60,l=60,r=50,pad=5,autoexpand=True),
        height=400,width=800    
        )
    
    fig = go.Figure(data=data, layout=layout)
    
    if offline:
        from plotly.offline import init_notebook_mode,plot
        init_notebook_mode()
        plot(fig)
    else:
        py.iplot(fig, filename='QS/sleep-detailed')
        
    #plotly.offline.iplot(fig) #, filename='stacked-subplots')
    
if __name__=='__main__':
    sleepdetailed_plotly(offline=True)
    #sleepdetailed_plotly()