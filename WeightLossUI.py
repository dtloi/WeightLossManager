import pyodbc
import WeightCalculations as wc
import GraphWLDB as gwl
from datetime import date, datetime
from pandas import read_csv, read_sql_query
from WeightLossDB import WeightLossDB


# a command-line User Interface to interact with the WeightLoss database (using WeightLossDB superclass)
class WeightLossUI(WeightLossDB):
	def __init__(self):
		WeightLossDB.__init__(self)
		# a bottom border for command-line text-prompts in UI
		self._border = "------------------------------------------"

		# start WeightLoss program
		print("\nWelcome to WeightLoss 2000!", end="\n\n")
		print("Please choose one of the following:")
		print("1 - New User\n2 - Load Progress")
		ans = int(input(self._border+'\n\n'))

		# new user
		if ans == 1:

			userIndex = self.newUserFromUI()

			# insert user's first log entry into database
			self.addEntryLogFromUI(userIndex)

		# load previous-user's information
		elif ans == 2:
			self.loadFromUI()

		else:
			print("Error..."); exit()



	####################################################################################################
	# add the users's entry to the database with the date and their current weight
	def addEntryLogFromUI(self, uid):

	# create the log-ID IPK (lid) for this entry
		self.cursor.execute("SELECT MAX(lid) FROM EntryLogs;")
		oldIndex = self.cursor.fetchall()[0][0]
		index = int(oldIndex) + 1 if oldIndex is not None else 1

		format1 = "%m/%d/%Y"
		date = input("Enter the date for your current entry (mm/dd/yyyy): ")
		weight = float(input("Enter your weight for your current entry (in lbs): "))
		self.cursor.execute( "INSERT INTO EntryLogs (lid, uid, date, weight) VALUES (?, ?, ?, ?);",
							(index, uid, datetime.strptime(date, format1), weight) )
	####################################################################################################



	####################################################################################################
	# enter a new user into the WeightLoss database
	# returns the new user's uid
	def newUserFromUI(self):
		print("Please enter the following information:")
		name = input("Name: ")
		sex = input("Sex (M/F): ")
		height = input("Height (in inches): ");

		# convert user's birthday to datetime format
		birthday = input("Birthdate (mm/dd/yyyy): ");  print()
		format1 = "%m/%d/%Y"

		# get index (uid) for placing this user in the database
		self.cursor.execute("SELECT MAX(uid) FROM Users;")
		oldIndex = self.cursor.fetchall()[0][0]
		index = int(oldIndex) + 1 if oldIndex is not None else 1

		# insert user's information into database
		self.cursor.execute( "INSERT INTO Users (uid, name, sex, birthday, height) VALUES (?, ?, ?, ?, ?);",
					(index, name, sex, datetime.strptime(birthday, format1), height) )

		return index
	### end newUserFromUI
	####################################################################################################


	####################################################################################################
	### retrieve and confirm a user's account
	def findUserFromUI(self):
		hasID = input("Do you have your User ID? (Y/N): ").upper()
		flag = True
		uid = None
		format1 = "%m/%d/%Y"

		# if the user knows their User ID number
		if hasID == 'Y':
			data = None
			while flag:
				uid = int(input("Enter your User ID: ")); print()
				self.cursor.execute("SELECT * FROM Users WHERE uid=?;", (uid))
				data = self.cursor.fetchall()

				if data is not None:
					date = data[0][3].split("-")
					data[0][3] = date[1] + "/" + date[2] + "/" + date[0]
					print("The account associated with that ID is:\n(ID, Name, Sex, Birthday, Height)"
						+ "\n%s\n%s" % (self._border, data[0]))

					correct = input("\nIs this information correct? (Y/N): ").upper()
					if correct == 'Y':
						flag = False

				else:
					print("Error: user ID not found. Please try again.")


		# if the user does not know their User ID number
		elif hasID == 'N':
			while flag:
				name = "%" + input("Please enter your name: ") + "%"
				self.cursor.execute("SELECT * FROM Users WHERE name LIKE ?;", name)
				data = self.cursor.fetchall()

				# if only one record was found
				if len(data) == 1:
					date = data[0][3].split("-")
					data[0][3] = date[1] + "/" + date[2] + "/" + date[0]
					rec = input("\nThe only record found is:\n(ID, Name, Sex, Birthday, Height)"
							+ " = %s.\n\nIs this correct? (Y/N): " % data[0]).upper()
					if rec == 'Y':
						flag = False
						uid = int(data[0][0])

				# if there are multiple names similar to the given name
				elif len(data) > 1:
					print("\nThe following records were found:\n")
					print("(ID, Name, Sex, Birthday, Height)\n%s" % self._border)
					for i in range(len(data)):
						date = data[i][3].split("-")
						data[i][3] = date[1] + "/" + date[2] + "/" + date[0]
						print("%s" % data[i])

					uid = int(input("\nPlease enter the ID number of your account, or press 0 to try again: "))
					if uid in [data[i][0] for i in range(len(data))]:
						flag = False


				else:
					print("No records with the name %s were found, please re-enter your name." % name[1:-1])


		else:
			print("Input error."); exit()

		return uid
	### end findUserFromUI
	####################################################################################################


	####################################################################################################
	### load a user's files from their uid number using a command-line User Interface
	def loadFromUI(self):
		uid = self.findUserFromUI()
		print("\nWhat would you like to do next?")
		print("1 - Add New Entry\n2 - Graph Progress")
		userChoice = int(input(self._border + "\n\n"))

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

		else:
			print("Error..."); exit()
	### end loadFromUI
	####################################################################################################
