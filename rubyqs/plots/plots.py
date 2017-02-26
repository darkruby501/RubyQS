# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 21:21:46 2016

@author: RMB
"""

## Regular Imports
from datetime import timedelta


#plotly.offline.init_notebook_mode() # run at the start of every notebook

def xrange(df):
    return [df.index[0]-timedelta(days=1),df.index[-1]+timedelta(days=1)]

def lastNdays(df,N):
        return df[df.index[-1]+timedelta(days=-N):df.index[-1]]

def lastNrange(df,N,plus1=False):
    last = df.index[-1].timestamp()*1000
    if plus1:
        last += 1*1800*24000 #for graphs which get cut off
    return [last-N*3600*24000,last]


N = 14


colors = {
    'vprod':"#2f78bd",
    'vunprod':"#c5392f",
    'neutral':"#655568",
    'deep':'#0d4857',
    'rem':'#8ad3e5',
    'light':'#518087',
    'intrpt':'#b2b2b2',
    'toss':'#c0bfb7',
    'nap':'#F0D99C',
    'intrpt2':'#BEBEBE',
    'steps':"#f0bd6e",
    'vigor':"#784f99",
    'heartrate':"#f47d33",
    'calories':"#50af43",
    'workflowy':'#3f8cc3'
    }
