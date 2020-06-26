import click
from WeightLossDB import WeightLossDB
from WeightLossUI import WeightLossUI



# program runs UI if no command-line arguments are given with click
@click.command()
@click.option('--csv', default=None, help='The CSV filepath for the list of new user-entries')


def main(csv):

	# start user interface if command-line args are None
	if csv is None:
		ui = WeightLossUI()

	# add a user's entry logs from CSV file to database
	else:
		wloss = WeightLossDB()

		# if the CSV data was successfully inserted into database
		if wloss.csvEntryLog(csv):
			print("\nNew entries successfully added to database.\n")

		else:
			print("\nError: username and password incompatible. No entries added.\n")


if __name__ == '__main__': main()
