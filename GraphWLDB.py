import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import timedelta
from datetime import datetime as dt
from pandas import DataFrame
from decimal import Decimal



# graph the user's weight data over time compared to their projected weight-loss
# using a "lost lbs. per week" plan
def GraphByPlan(dateDF, name, weeklyLoss):

	fig, ax  =  plt.subplots(figsize=(11,9))

	# construct dataframe for weight-loss plan for comparison
	wlpDF = dateDF.copy()
	firstWeight = dateDF['weight'].values[0]
	firstDate = dt.strptime(dateDF['date'].values[0], "%Y-%m-%d").date()

	# iterate through copy and change weights to projected 
	for index, row in wlpDF.iterrows():
		thisDate = dt.strptime(row['date'], "%Y-%m-%d").date()
		dateDifference = (thisDate - firstDate).days
		wlpDF.at[index, 'weight'] = firstWeight - (weeklyLoss/7)*dateDifference

	# plot user's weight
	ax.plot('date', 'weight', data=dateDF, label="Actual Weight", marker='o', color='red')
	ax.plot('date', 'weight', data=dateDF, label="_nolegend_", color='red')

	# plot projected weight
	ax.plot('date', 'weight', data=wlpDF, label="Projected (at %s lbs. per week)"
			% Decimal(round(weeklyLoss,1)), marker='o', color='blue')
	ax.plot('date', 'weight', data=wlpDF, label="_nolegend_", color='blue')

	# adjust plot settings
	ax.set_title("%s's Weight  (in lbs.)" % name, fontsize=18)
	ax.legend(loc="upper right")
	ax.set_xlabel("Date", fontsize=15)
	ax.set_ylabel("Weight", fontsize=15)
	ax.grid(True)

	# rotates and right aligns the x labels, and moves the bottom of the
	# axes up to make room for them
	fig.autofmt_xdate()

	plt.show()
