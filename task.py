# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 20:06:43 2016
test
@author: RMB
"""
import logging

from basis import Basis

from rubyqs.plots import *
from rubyqs.rescuetime import RescueTime

LOG_PATH = r"C:\Users\RMB\Drive\Tsuyoku\QS Data\QuantifedSelf" \
    r"\RubyQS.log"



## QS Task

# 1) APIs->Preparation->DB

# 2) DB(->Processing)->Plotting

# RescueTime

def QSdaily(download=False,plotting=False,store=False):
    logging.basicConfig(filename=LOG_PATH,level=logging.DEBUG,
							format='%(asctime)s %(message)s',
							datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('rubyqs periodic task started.')


    if download:
        logging.debug('Download started.')
        RT = RescueTime(store=True)
        r = RT.get_rescuetime_log()
        Basis
        BC = Basis(store=True,store_raw=True)
        b = BC.get_all()

    # Plotting
    if plotting:
        logging.debug('Plotting in main task started.')

        #rollingtable_plotly()
        dayssince_plotly()
        activitydaily_plotly()
        prodhours_plotly()
        heatmap_plotly()
        sleepdetailed_plotly()
        sleeptimes_plotly()

    if 'r' not in locals():
        r = None
    if 'b' not in locals():
        b = None

    return (r,b)


if __name__=='__main__':

    try:
        QSdaily(download=True,plotting=True,store=True)
        print('QS success!')
        logging.info('rubyqs periodic successfully complete!')
    except BaseException as e:
        logging.exception('rubyqs failed: ' + str(e))
