import click
from WeightLossDB import WeightLossDB
from WeightLossUI import WeightLossUI



# program runs UI if no command-line arguments are given with click
@click.command()
@click.option('--usercsv', default=None, help='The CSV filepath for the list of new users')
@click.option('--entrycsv', default=None, help='The CSV filepath for the list of new user-entries')


def main(usercsv, entrycsv):

	# start user interface if command-line args are None
	if usercsv is None and entrycsv is None:
		ui = WeightLossUI()

	else:

		wloss = WeightLossDB()

		# store new users in database
		if usercsv is not None:
			wloss.newUser(usercsv)
			print("New users data successfully added to database.")

		# store new entries in database
		if entrycsv is not None:
			wloss.addEntryLog(entrycsv)
			print("New entries successfully added to database.")



if __name__ == '__main__': main()
