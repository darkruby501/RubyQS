from plots.plots import *

def dayssince_plotly(offline=False):

    df = query("""
            SELECT 
                SUBSTR(localdate,1,10) AS localtime, 
                CAST(SUM(seconds) AS FLOAT)/60 AS minutes,
                CAST(SUM(seconds) AS FLOAT)/3600 AS hours
            FROM rescuetime_log 
            WHERE LOWER(document) LIKE '%journal of strategy%'
            GROUP BY localtime
            --HAVING minutes > 10
            ORDER BY localdate
            """,
            Basis._DB_PATH,parse_dates=['localtime'],index_col='localtime')
    
    df = df['minutes'] #extract relevant series
    days_since_rationality10 = (date.today() - df[df>10].index[-1].date()).days
    days_since_rationality30 = (date.today() - df[df>30].index[-1].date()).days
    
    
    df = query("""
            SELECT 
                SUBSTR(localdate,1,10) AS localtime, 
                CAST(SUM(seconds) AS FLOAT)/60 AS minutes
                --CAST(SUM(seconds) AS FLOAT)/3600 AS hours
            FROM rescuetime_log 
            WHERE LOWER(activity) LIKE '%workflowy%'
            GROUP BY localtime
            --HAVING minutes > 10
            ORDER BY localdate
            """,
            Basis._DB_PATH,parse_dates=['localtime'],index_col='localtime')
    
    df = df['minutes'] #extract relevant series
    days_since_workflowy10 = (date.today() - df[df>5].index[-1].date()).days
    days_since_workflowy30 = (date.today() - df[df>30].index[-1].date()).days
    
    
    df = query("""
            SELECT date(datetime(date_iso,PRINTF('%.0d',substr(tz_offset,1))||' hours')) 
                AS local_time,COUNT(*) AS minutes
            FROM biosignals
            WHERE heartrate > 135 AND steps > 60
            GROUP BY local_time
            """,
            Basis._DB_PATH,parse_dates=['local_time'],index_col='local_time'
              )
        
    df = df['minutes']
    days_since_vigorous10 = (date.today() - df[df>2].index[-1].date()).days
    
    
    df = pd.DataFrame(index=[
            'Rationality Review 30min',
            'Rationality Review 10min',
#            'Workflowy 30min',
            'Workflowy 5min',
            'Vigorous Exercise'
        ],
          data = {
            'X':[days_since_rationality30,days_since_rationality10,
                 days_since_workflowy10,
                 days_since_vigorous10],
            'color':['k','k',colors['workflowy'],colors['vigor']]
        }
            
    )
 
    Bars = go.Bar(
        x=df['X'],
        y=df.index,
        orientation='h',
        marker=dict(color=df['color']),
        showlegend=False,
        )
        
    
    layout = go.Layout(
        barmode='stack',
        yaxis=dict(
            tickfont={
                'size':18,
                'family':"Open Sans, sans-serif"
            },
            titlefont={
                'size':20
            },
            showgrid=True,
            gridwidth=1.3,
            gridcolor="rgb(102, 102, 102)",
            fixedrange=True,
        ),
        yaxis2=dict(
            overlaying="y",
            side="left",
            anchor="free",
            position=0,
            type="category",
            autorange=False,
            range=[.05,.8],
            showexponent="none",
            fixedrange=True,
            showticklabels=False
        ),
        xaxis=dict(title='Days',
           autorange=True,
           tickfont={
            'size':18,
            },
        ),
        title='Days Since . . .',
        margin=dict(t=80,b=60,l=240,r=30,pad=5,autoexpand=True),
        #height=400,width=800    
    )
    
    
    tline1 = go.Scatter(x=[7]*2,
                        y=[-2,18],
                           showlegend=False,yaxis="y2",hoverinfo="none",
                    line=dict(color=("red"),width=4,dash='solid'),mode='lines')
    
    tline2 = go.Scatter(x=[3]*2,
                        y=[-2,18],
                           showlegend=False,yaxis="y2",hoverinfo="none",
                    line=dict(color=("red"),width=4,dash='dash'),mode='lines')
    
                           
    data = [Bars,tline1,tline2]
    
    fig = go.Figure(data=data, layout=layout)
 
 

    if offline:
        from plotly.offline import init_notebook_mode,plot
        init_notebook_mode()
        plot(fig)
    else:
        py.iplot(fig, filename='QS/rolling-table')
    
if __name__=='__main__':
    dayssince_plotly(offline=True)