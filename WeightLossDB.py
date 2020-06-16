import pyodbc
from datetime import date
from WeightCalculations import CaloricNeeds


class WeightLossDB:

	####################################################################################################
	### init
	def __init__(self):
		# connect to SQL Server
		conn = None
		try:
			conn = pyodbc.connect('Driver={SQL Server};'
							'Server=DESKTOP-NPQM960;'
							'Trusted_Connection=yes;')
			print("Successfully connected to SQL Server!")

		except:
			print("Connection to SQL Server failed!");  exit()

		if conn is not None:
			conn.autocommit = True

		# place cursor on WeightLoss database
		self._cursor = conn.cursor()
		self._cursor.execute("SELECT name FROM master.dbo.sysdatabases where name=?;", ("WeightLoss"))

		data = self._cursor.fetchall()

		# if database exists
		if data:
			print("Database found successfully.")

		# if database does not exist, create database and tables
		else:
			print("WeightLoss database does not yet exist....creating...")
			self._cursor.execute("CREATE DATABASE WeightLoss")
			self._cursor.execute("CREATE TABLE Users (uid INTEGER PRIMARY KEY, name varchar(20), gender CHAR(1), "
						+ "birth TEXT, height real, CHECK (gender in ('M', 'F')) "
						+ "CHECK (height > 0));")

			self._cursor.execute("CREATE TABLE EntryLogs (uid INTEGER, day INTEGER, month INTEGER, "
						+ "year INTEGER, weight real, PRIMARY KEY (uid, day, month, year), "
						+ "FOREIGN KEY (uid) REFERENCES Users ON DELETE CASCADE ON UPDATE CASCADE, "
						+ "CHECK (day < 32 AND day > 0 AND month < 13 AND month > 0 "
						+ "AND weight > 0));")

		# start WeightLoss program
		self._border = "------------------------------------------"
		print("\nWelcome to WeightLoss 2000!", end="\n\n")
		print("Please choose one of the following:")
		print("1 - New User\n2 - Load Progress")
		ans = int(input(self._border+'\n\n'))

		if ans == 1:
			self.newUser()
		elif ans == 2:
			self.load()
		else:
			print("Error..."); exit()
		
	### end init
	####################################################################################################


	####################################################################################################
	# add the users's entry to the database with the date and their current weight
	def addEntryLog(self, uid, date, weight):
		self._cursor.execute( "INSERT INTO EntryLogs (uid, day, month, year, weight) VALUES (?, ?, ?, ?, ?);",
					(uid, date[0], date[1], date[2], weight) )
	####################################################################################################



	####################################################################################################
	# enter a new user into the WeightLoss database
	def newUser(self):
		print("Please enter the following information:")
		name = input("Name: ")
		gender = input("Gender (M/F): ")
		birthdate = input("Birthdate (mm/dd/yyyy): ")
		height = float(input("Height (in centimeters): "))
		weight = float(input("Current weight (in kg): "))

		# get index (uid) for placing this user in the database
		self._cursor.execute("SELECT MAX(uid) FROM Users;")
		old = self._cursor.fetchall()[0][0]
		index = int(old) + 1 if old is not None else 1

		# get current date
		curr_date = self._format_date()

		# insert user's information into database
		self._cursor.execute( "INSERT INTO Users (uid, name, gender, birthdate, height) "
							+ "VALUES (?, ?, ?, ?, ?);", (index, name, gender, birthdate, height) )

		# insert user's first log entry into database
		self.addEntryLog(index, curr_date, weight)
	### end newUser
	####################################################################################################


	####################################################################################################
	### retrieve and confirm a user's account
	def findUser(self):
		s = input("Do you have your User ID? (Y/N): ").upper()
		flag = True
		uid = None

		# if the user knows their User ID number
		if s == 'Y':
			data = None
			while flag:
				uid = int(input("Enter your User ID: ")); print()
				self._cursor.execute("SELECT * FROM Users WHERE uid=?;", (uid))
				data = self._cursor.fetchall()

				if data is not None:
					print("The account associated with that ID is:\n"
						+ "(ID, Name, Gender, Birthdate, Height)\n%s\n%s" % (self._border, data[0]))

					c = input("\nIs this information correct? (Y/N): ").upper()
					if c == 'Y':
						flag = False

				else:
					print("Error: user ID not found. Please try again.")


		# if the user does not know their User ID number
		elif s == 'N':
			while flag:
				name = "%" + input("Please enter your name: ") + "%"
				self._cursor.execute("SELECT * FROM Users WHERE name LIKE ?;", name)
				data = self._cursor.fetchall()

				# if only one record was found
				if len(data) == 1:
					inp = input("\nThe only record found is:\n(ID, Name, Gender, Birthdate, Height)"
							+ " = %s.\n\nIs this correct? (Y/N): " % data[0]).upper()
					if inp == 'Y':
						flag = False

				# if there are multiple names similar to the given name
				elif len(data) > 1:
					print("\nThe following records were found:\n")
					print("(ID, Name, Gender, Birthdate, Height)\n%s" % self._border)
					for i in range(len(data)):
						print("%s" % data[i])

					uid = int(input("\nPlease enter the ID number of your account, or press 0 to try again: "))
					if uid in [data[i][0] for i in range(len(data))]:
						flag = False


				else:
					print("No records with the name %s were found, please re-enter your name." % name[1:-1])


		else:
			print("Input error."); exit()

		return uid
	### end findUser
	####################################################################################################


	####################################################################################################
	### load a user's files from their uid number
	def load(self):
		uid = self.findUser()
		print("\nWhat would you like to do next?")
		print("1 - Add New Entry\n2 - Graph Progress")
		u = int(input(self._border + "\n\n"))

		# add new entry
		if u == 1:
			date = self.__format_date()
			weight = float(input("Enter your current weight (in kg): "))
			self._cursor.execute("INSERT INTO EntryLogs (uid, day, month, year, weight) "
								+ "VALUES (?, ?, ?, ?, ?);", (uid, date[0], date[1], date[2], weight))

		elif u == 2:

		else:
			print("Error..."); exit()
	### end load
	####################################################################################################


	# private helper to retrieve the current date and reformat it from yyyy/mm/dd to dd/mm/yyyy
	def __format_date(self):
		curr_date = str(date.today()).split('-')
		return [int(curr_date[2]), int(curr_date[1]), int(curr_date[0])]


if __name__ == '__main__':
	wl = WeightLossDB()
