# -*- coding: utf-8 -*-
"""
"""

from plots.plots import *

def prodhours_plotly(offline=False):
    df = RescueTime().get_rescuetime_days()
    
    df = df[['Productive','Unproductive']]
    #df.iloc[-1]=np.nan #ignore current incomplete day
    
    trace1 = go.Bar(
            x=df.index,
            y=df['Productive'],
            name='Productive',
            marker={'color':colors['vprod']}
            )
    trace2 = go.Scatter(
            x=df.index,
            y=df['Unproductive'],
            name='Unproductive',
            mode='markers',
            line=dict(color=colors['vunprod'],width=3,dash='solid'),
                      marker=dict(size=8),
            opacity=0.9
            )
    
    tline1 = go.Scatter(x=xrange(df),y=[7]*2,name='target hours',showlegend=False,
                line=dict(color=("rgb(0, 0, 0)"),width=2,dash='dot'),mode='lines')
    tline2 = go.Scatter(x=xrange(df),y=[4]*2,name='target hours',showlegend=False,
                line=dict(color=("red"),width=2,dash='dot'),mode='lines')
                
    data = [trace1,trace2,tline1,tline2]
    layout = go.Layout(
        yaxis=dict(tickformat='.1f',tickmode="linear",dtick=1,fixedrange=True,title='Hours'),
        xaxis=dict(showgrid=True,tickformat='%m-%d',hoverformat='%b-%d',
                   autorange=False,range=lastNrange(df,N,plus1=True),
                   tickmode="linear",dtick=86400000*1),
        title='Daily Productivity',
        margin=dict(t=60,b=60,l=60,r=50,pad=5,autoexpand=True),
        height=400,width=800    
        )
    
    fig = go.Figure(data=data, layout=layout)
    
    if offline:
        from plotly.offline import init_notebook_mode,plot
        init_notebook_mode()
        plot(fig)
    else:
        py.iplot(fig, filename='QS/prod-hours') #, fileopt='extend')
    
if __name__=='__main__':
    prodhours_plotly(offline=True)