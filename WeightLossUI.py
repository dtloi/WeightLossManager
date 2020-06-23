import pyodbc
import WeightCalculations as wc
import GraphWLDB as gwl
from datetime import date, datetime
from pandas import read_csv, read_sql_query
from WeightLossDB import WeightLossDB
from decimal import Decimal
from time import sleep


# a command-line User Interface to interact with the WeightLoss database (using WeightLossDB superclass)
class WeightLossUI(WeightLossDB):
	def __init__(self):

		WeightLossDB.__init__(self)

		# a bottom border for command-line text-prompts in UI
		self.border = "-------------------------------------------------"

		# the format for displaying dates to the user
		self.USformat = "%m/%d/%Y"

		# start WeightLoss program
		print("\nWelcome to WeightLoss Manager!", end="\n\n")
		print("Please choose one of the following:")
		print("1 - New User\n2 - Load Progress")
		ans = int(input(self.border+'\n\n'))

		# new user
		if ans == 1:

			userIndex = self.newUserFromUI()

			# insert user's first log entry into database
			self.addEntryLogFromUI(userIndex)

		# load previous-user's information
		elif ans == 2:
			uid = self.findUserFromUI()
			self.loadFromUI(uid)

		else:
			print("Error..."); exit()



	# add the users's entry to the database with the date and their current weight
	def addEntryLogFromUI(self, uid):

		# insert into database
		date = input("Enter the date for your current entry (mm/dd/yyyy): ")
		weight = float(input("Enter your weight for your current entry (in lbs): "))
		self.cursor.execute( "INSERT INTO EntryLogs (uid, date, weight) VALUES (?, ?, ?);",
							(uid, datetime.strptime(date, self.USformat), weight) )



	# enter a new user into the WeightLoss database
	# returns the new user's uid
	def newUserFromUI(self):
		print("Please enter the following information:")
		name = input("Name: ")
		sex = input("Sex (M/F): ")
		height = input("Height (in inches): ");

		# convert user's birthday to datetime format
		birthday = input("Birthdate (mm/dd/yyyy): ");  print()
		self.format = "%m/%d/%Y"

		# get index (uid) for placing this user in the database
		self.cursor.execute("SELECT MAX(uid) FROM Users;")
		oldIndex = self.cursor.fetchall()[0][0]
		index = int(oldIndex) + 1 if oldIndex is not None else 1

		# insert user's information into database
		self.cursor.execute( "INSERT INTO Users (uid, name, sex, birthday, height) VALUES (?, ?, ?, ?, ?);",
					(index, name, sex, datetime.strptime(birthday, self.format), height) )

		return index




	# retrieve and confirm a user's account
	def findUserFromUI(self):
		hasID = input("Do you have your User ID? (Y/N): ").upper()
		flag = True
		uid = None

		# if the user knows their User ID number
		if hasID == 'Y':
			data = None
			while flag:
				uid = int(input("Enter your User ID: ")); print()
				data = read_sql_query("SELECT * FROM Users WHERE uid=?;", con=self.connection, params=(uid,))

				if data is not None:
					print("The account associated with that ID is:\n%s\n%s" % (data.to_string(index=False), self.border))

					correct = input("\nIs this information correct? (Y/N): ").upper()
					if correct == 'Y':
						flag = False

				else:
					print("Error: user ID not found. Please try again.")


		# if the user does not know their User ID number
		elif hasID == 'N':
			while flag:
				name = "%" + input("Please enter your name: ") + "%"
				data = read_sql_query("SELECT * FROM Users WHERE name LIKE ?;", con=self.connection, params=(name,))

				# if only one record was found
				if len(data) == 1:
					rec = input("\nThe only record found is:\n%s\n%s.\n\nIs this correct? (Y/N): " % (data.to_string(index=False), self.border)).upper()
					if rec == 'Y':
						flag = False
						uid = int(data['uid'].iloc[0])

				# if there are multiple names similar to the given name
				elif len(data) > 1:
					print("\nThe following records were found:\n%s\n%s" % (data.to_string(index=False), self.border))

					uid = int(input("\nPlease enter the UID number of your account, or press 0 to try again: "))
					# if a valid option has been selected
					if uid in data['uid'].tolist():
						flag = False

				else:
					print("No records with the name %s were found, please re-enter your name." % name[1:-1])


		else:
			print("Input error."); exit()

		return uid



	# load a user's files from their uid number using a command-line User Interface
	def loadFromUI(self, uid):
		print("\nWhat would you like to do next? (enter a number)")
		print("1 - Add New Entry\n2 - Graph Progress\n3 - Weight Estimator\n4 - Help")
		userChoice = int(input(self.border + "\n\n"))

		# add new entry
		if userChoice == 1:
			self.addEntryLogFromUI(uid)

		# graph user's progress
		elif userChoice == 2:
			# read query results into pandas dataframe
			df = read_sql_query("SELECT date, weight FROM EntryLogs WHERE uid=? ORDER BY CONVERT(DATE, date) ASC;",
								con=self.connection, params=(uid,))
			name = self.cursor.execute("SELECT name FROM Users WHERE uid=?;", (uid)).fetchall()[0][0]
			gwl.byMonth(df, name)  # test graph by month

		# display weight-loss estimation for a given date (in lbs.)
		elif userChoice == 3:
			today = datetime.strftime(datetime.today(), self.USformat)
			currentDate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
			self.cursor.execute("SELECT weight FROM EntryLogs WHERE uid=? AND date=?;",(uid, currentDate))
			data = self.cursor.fetchall()

			# the user needs to have an entry log for the current date
			while len(data) == 0:
				print("You must first enter an entry log for today's date (%s)..." % today)
				self.addEntryLogFromUI(uid)
				self.cursor.execute("SELECT weight FROM EntryLogs WHERE uid=? AND date=?;",(uid, currentDate))
				data = self.cursor.fetchall()

			# the user's current weight
			weightNow = round(data[0][0], 3)

			futureDate = input("Enter the future date for your desired weight-estimation (mm/dd/yyyy): ")
			weeklyLoss = 2.1
			while weeklyLoss > 2 and weeklyLoss > 0:
				weeklyLoss = float(input("Enter your desired weight loss (in lbs/week, and <=2): "))

			weightLoss = wc.lbsLost(futureDate, weeklyLoss, dateFormat=self.USformat)
			loss, weightLoss  =  round(weeklyLoss, 3), round(weightLoss, 3)
			weightLater = round(weightNow - weightLoss, 3)

			print( "\nOn %s at the rate of %s lbs per week, you will have lost %s lbs." % (futureDate, weeklyLoss, weightLoss))
			print("%s --> %s" % (weightNow, weightLater))
			print(self.border + "\n")


		# print help messages
		elif userChoice == 4:
			print("\n" + self.border + "\nAdd New Entry: adds a new log entry to record the date and the user's weight")
			print("Graph Progress: graphs the user's weight progress over a period of time")
			print("Weight Estimator: calculate the user's weight on a given date at their current weight-loss rate (lbs. per week)")
			print(self.border + "\n")
			sleep(2)
			self.loadFromUI(uid)  # restart menu

		else:
			print("Error: user choice must be one of the numbers above");  exit()
