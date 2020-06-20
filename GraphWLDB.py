import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas.io.sql as psql
from datetime import datetime
from numpy import fromiter, datetime64, timedelta64



def byMonth(data, name, datemin=None, datemax=None):

	if datemin is None:
		datemin = data['date'][0]
	if datemax is None:
		datemax = data['date'][len(data)-1]
	
	years = mdates.YearLocator()   # every year
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()
	monthsFormat = mdates.DateFormatter('%B')
	fig, ax  =  plt.subplots(figsize=(11,9))
	# must account for if over a year, then months code will not work

	ax.plot('date', 'weight', data=data)
	ax.set_title("%s's Weight  (in lbs.)" % name, fontsize=18)

	# round to nearest months

	ax.set_xlim(datemin, datemax)

	# format the coords message box
	ax.format_xdata = mdates.DateFormatter("%m/%d/%Y")
	ax.format_ydata = lambda x: '$%1.2f' % x
	ax.grid(False)

	# rotates and right aligns the x labels, and moves the bottom of the
	# axes up to make room for them
	fig.autofmt_xdate()

	plt.show()

