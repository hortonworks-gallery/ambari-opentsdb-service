# Code taken from http://trading.cheno.net/wp-content/uploads/2011/12/google_intraday.py
# See for more info: http://trading.cheno.net/downloading-google-intraday-historical-data-with-python/
# Copyright (c) 2011, Mark Chenoweth
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted 
# provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following 
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS 
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
import urllib,time,datetime,sys


class Quote(object):
  
  DATE_FMT = '%Y-%m-%d'
  TIME_FMT = '%H:%M:%S'
  
  def __init__(self):
    self.symbol = ''
    self.date,self.time,self.open_,self.high,self.low,self.close,self.volume = ([] for _ in range(7))

  def append(self,dt,open_,high,low,close,volume):
    self.date.append(dt.date())
    self.time.append(dt.time())
    self.open_.append(float(open_))
    self.high.append(float(high))
    self.low.append(float(low))
    self.close.append(float(close))
    self.volume.append(int(volume))
      
  def to_csv(self):
    return ''.join(["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(self.symbol,
              self.date[bar].strftime('%Y-%m-%d'),self.time[bar].strftime('%H:%M:%S'),
              self.open_[bar],self.high[bar],self.low[bar],self.close[bar],self.volume[bar]) 
              for bar in xrange(len(self.close))])
    
  def write_csv(self,filename):
    with open(filename,'w') as f:
      f.write(self.to_csv())
        
  def read_csv(self,filename):
    self.symbol = ''
    self.date,self.time,self.open_,self.high,self.low,self.close,self.volume = ([] for _ in range(7))
    for line in open(filename,'r'):
      symbol,ds,ts,open_,high,low,close,volume = line.rstrip().split(',')
      self.symbol = symbol
      dt = datetime.datetime.strptime(ds+' '+ts,self.DATE_FMT+' '+self.TIME_FMT)
      self.append(dt,open_,high,low,close,volume)
    return True

  def __repr__(self):
    return self.to_csv()

class GoogleIntradayQuote(Quote):
 				
  ''' Intraday quotes from Google. Specify interval seconds and number of days '''
  def __init__(self,symbol,interval_seconds=300,num_days=5):				
    super(GoogleIntradayQuote,self).__init__()
    self.symbol = symbol.upper()
    url_string = "http://www.google.com/finance/getprices?q={0}".format(self.symbol)
    url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_seconds,num_days)
    csv = urllib.urlopen(url_string).readlines()
    for bar in xrange(7,len(csv)):
      if csv[bar].count(',')!=5: continue
      offset,close,high,low,open_,volume = csv[bar].split(',')
      if offset[0]=='a':
        day = float(offset[1:])
        offset = 0
      else:
        offset = float(offset)
      open_,high,low,close = [float(x) for x in [open_,high,low,close]]
      dt = datetime.datetime.fromtimestamp(day+(interval_seconds*offset))
      self.append(dt,open_,high,low,close,volume)

       
if __name__ == '__main__':

  f = open('opentsd.input', 'a')
  
  if len(sys.argv) > 1:
    stocks = sys.argv[1]
  else:
    stocks = ("AAPL")
  for stock in stocks.split(','):
    if 'quotes' in locals():
       del(quotes)
    quotes = GoogleIntradayQuote(stock,60,300)
    #atts = [a for a in dir(quotes) if not a.startswith('__')]    
    #print atts
    for i in range(len(quotes.high)):
      #from dateutil import parser    
      #datetime_str = str(quotes.date[i]) + ' ' + str(quotes.time[i]) + ' PST'
      #dt = parser.parse(datetime_str)
      from datetime import datetime
      datetime_str = str(quotes.date[i]) + '-' + str(quotes.time[i])

      dt = datetime.strptime(datetime_str,"%Y-%m-%d-%H:%M:%S")
      td = (dt - datetime(1970, 1, 1))
      epoch_time = (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6 

      
      #print 'open '   + str(epoch_time) + ' ' + str(quotes.date[i]) + ' '  + str(quotes.time[i]) + ' ' + str(quotes.open_[i]) + ' symbol=' + str(quotes.symbol)      
      print ('open '   + str(epoch_time) + ' ' + str(quotes.open_[i]) + ' symbol=' + str(quotes.symbol), file=f)      
      print ('close '  + str(epoch_time) + ' ' + str(quotes.close[i]) + ' symbol=' + str(quotes.symbol), file=f)    
      print ('high '  + str(epoch_time) + ' ' + str(quotes.high[i]) + ' symbol=' + str(quotes.symbol), file=f)           
      print ('low '  + str(epoch_time) + ' ' + str(quotes.low[i]) + ' symbol=' + str(quotes.symbol), file=f)          
      print ('volume '  + str(epoch_time) + ' ' + str(quotes.volume[i]) + ' symbol=' + str(quotes.symbol), file=f)

  print (quotes)    
  f.close()
    
    
