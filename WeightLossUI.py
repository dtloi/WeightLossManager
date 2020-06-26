import pyodbc
import re
import getpass
import WeightCalculations as wc
import GraphWLDB as gwl
from datetime import date, datetime, timedelta
from pandas import read_csv, read_sql_query, to_datetime
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

		# option to create new user
		if ans == 1:
			self.__newUser()

		# option to access previous-user's account
		elif ans == 2:

			# get user's uid number
			uid = None
			while uid is None:
				uid = self.__findUID()

				# if the username/password combination was not found in database
				if uid is None:
					print("Error: incorrect username/password combination. Please try again.\n")

			# once the user's account has been located, push them to the main menu
			self.__mainMenu(uid)


		else:
			print("Error: please choose one of the valid startup options")


#####################################################################################################################


	# get username from UI, check username character conditions
	def __username(self):
		userFlag, username  =  True, None
		while userFlag:

			username = input("Enter username: ")

			# match illegal username characters
			if len(re.findall(self.userPattern, username)) > 0:
				print("Error: username cannot start with a period, cannot contain spaces, and "
					+ "cannot contain the following characters: & = _ ' - + , < > ( )")

			else:
				userFlag = False

		return username


#####################################################################################################################


	# get password from UI, check password character conditions
	def __password(self):
		pwdFlag, pwd  =  True, None
		while pwdFlag:

			# password hidden from command-line when typed
			pwd = getpass.getpass(prompt="Enter password: ")

			# match illegal password characters
			if len(re.findall(self.passwordPattern, pwd)) > 0:
				print("Error: password cannot contain spaces")

			else:
				pwdFlag = False

		return pwd


#####################################################################################################################


	# retrieve the User ID (uid) for a user's account
	def __findUID(self):
		uid = None
		username = self.__username()
		pwd = self.__password()
		data = self.cursor.execute("SELECT uid FROM Users WHERE username=? AND password=HASHBYTES('SHA2_512', ?);",
				(username, pwd)).fetchall()
		if len(data) != 0:
			uid = int(data[0][0])

		return uid


#####################################################################################################################


	# add the users's entry to the database with the date and their current weight
	def __addEntryLog(self, uid):

		# insert into database
		date = input("Enter the date for your current entry (mm/dd/yyyy): ")
		weight = float(input("Enter your weight for your current entry (in lbs): "))
		self.cursor.execute( "INSERT INTO EntryLogs (uid, date, weight) VALUES (?, ?, ?);",
							(uid, datetime.strptime(date, self.USformat), weight) )


#####################################################################################################################


	# enter a new user into the WeightLoss database
	# returns the new user's uid
	def __newUser(self):
		print("\nHello new user.\nPlease provide us with the following information:")
		username = self.__username()
		pwd = self.__password()

		name = input("Name: ")
		sex = input("Sex (M/F): ")
		height = input("Height (in inches): ");

		# convert user's birthday to datetime format
		birthday = input("Birthdate (mm/dd/yyyy): ");  print()

		# get index (uid) for placing this user in the database
		self.cursor.execute("SELECT MAX(uid) FROM Users;")
		oldIndex = self.cursor.fetchall()[0][0]
		uid = int(oldIndex) + 1 if oldIndex is not None else 1

		# insert user's information into database with encrypted password
		self.cursor.execute( "INSERT INTO Users (uid,username,password,name,sex,birthday,height) "
							+ "VALUES (?,?,HASHBYTES('SHA2_512', ?),?,?,?,?);",
							(uid, username, pwd, name, sex, datetime.strptime(birthday,self.USformat), height) )

		return uid


#####################################################################################################################


	# read the number of pounds per week the user would like to use from UI
	def __weeklyLoss(self):
		weeklyLoss = 2.1
		while weeklyLoss > 2 and weeklyLoss > 0:
					weeklyLoss = float(input("Enter your desired weight loss (in lbs/week, and <=2): "))

		return weeklyLoss


#####################################################################################################################


	# return the weight of the user on today's date
	def __weightToday(self, uid):
		today = datetime.strftime(datetime.today(), self.USformat)
		currentDate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		self.cursor.execute("SELECT weight FROM EntryLogs WHERE uid=? AND date=?;",(uid, currentDate))
		data = self.cursor.fetchall()

		# the user needs to have an entry log for the current date
		while len(data) == 0:
			print("You must first enter an entry log for today's date (%s)..." % today)
			self.__addEntryLog(uid)
			self.cursor.execute("SELECT weight FROM EntryLogs WHERE uid=? AND date=?;",(uid, currentDate))
			data = self.cursor.fetchall()

		# the user's current weight
		return float(data[0][0])


#####################################################################################################################

	
	# brings user to the main menu so they can access application features
	def __mainMenu(self, uid):
		self.cursor.execute("SELECT username FROM Users WHERE uid=?;", (uid))
		username = self.cursor.fetchall()[0][0]
		flag = True

		# run continuous loop on main menu until user quits
		while flag:
			print("\nHello %s!" % username)
			print("What would you like to do next? (enter a number)\n")
			print("1 - Add New Entry\n2 - Graph Progress\n3 - Weight Estimator\n4 - Calorie Tracker\n5 - Help\n"
					+ "6 - Quit")
			
			userChoice = int(input(self.border + "\n\n"))

			# add new entry
			if userChoice == 1:
				self.__addEntryLog(uid)

			# graph user's progress
			elif userChoice == 2:
				# read query results into pandas dataframe
				graphDF = read_sql_query("SELECT date, weight FROM EntryLogs WHERE uid=? ORDER BY CONVERT(DATE, date) ASC;",
									con=self.connection, params=(uid,))
				dateDF = graphDF.copy()
				dateDF['date'] = to_datetime(dateDF['date'])
				name = self.cursor.execute("SELECT name FROM Users WHERE uid=?;", (uid)).fetchall()[0][0]

				# get required graph information
				print("\nYour progress will be graphed...")
				weeklyLoss = self.__weeklyLoss()
				startDate = input("Enter the starting date for the graph (mm/dd/yyyy): ").split("/")
				endDate = input("Enter the ending date for the graph (mm/dd/yyyy): ").split("/")

				# if dates input does not contain 0's for single digit months or single digit days, add them
				# (for string matching purposes)
				for i in range(len(startDate)-1):
					if len(startDate[i]) == 1:
						startDate[i] = "0" + startDate[i]
					if len(endDate[i]) == 1:
						endDate[i] = "0" + endDate[i]

				# reformat into datetime-style string
				startDate = startDate[2] + "-" + startDate[0] + "-" + startDate[1]
				endDate = endDate[2] + "-" + endDate[0] + "-" + endDate[1]

				# adjust end date by one day (for graph-padding)
				startDateDT = datetime.strptime(startDate, "%Y-%m-%d") - timedelta(1)
				endDateDT = datetime.strptime(endDate, "%Y-%m-%d")

				# get the start and end dates for graphing
				startIndex = dateDF[dateDF.date >= startDateDT].first_valid_index()
				endIndex = dateDF[dateDF.date >= endDateDT].first_valid_index()

				graphDF = graphDF.truncate(before=startIndex, after=endIndex)
				gwl.GraphByPlan(graphDF, name, weeklyLoss)  # test graph by month

			# display weight-loss estimation for a given date (in lbs.)
			elif userChoice == 3:

				# the user's current weight
				weightNow = Decimal(round(self.__weightToday(uid), 1))

				futureDate = input("Enter the future date for your desired weight-estimation (mm/dd/yyyy): ")
				weeklyLoss = Decimal(round(self.__weeklyLoss(), 1))

				# the amount of weight lost by the user
				weightLoss = round(wc.lbsLost(futureDate, weeklyLoss, dateFormat=self.USformat), 1)

				# the user's weight on the future date
				weightLater = round(weightNow - weightLoss, 1)

				print( "\nOn %s at the rate of %1.1f lbs per week, you will have lost %.1f lbs." % (futureDate, weeklyLoss, weightLoss))
				print("%.1f --> %.1f" % (weightNow, weightLater))
				print(self.border + "\n")

			# display the necessary caloric intake for a user given their desired weight loss schedule
			elif userChoice == 4:
				weeklyLoss = self.__weeklyLoss()
				weightNow = self.__weightToday(uid)
				df = read_sql_query("SELECT sex,birthday,height FROM Users WHERE uid=?;", con=self.connection, params=(uid,))

				# get user's age (rounded down regardless of months,days)
				date = datetime.strptime(df['birthday'].values[0], "%Y-%m-%d").date()
				timeDifference = datetime.today().date() - date
				age = timeDifference.days // 365

				# calculate user's maintenance calories
				# (their daily calorie intake at which they will remain their current weight)
				caloriesMaintain = wc.CaloricNeeds(df['sex'].values[0], age, weightNow, df['height'].values[0])
				print("In order to maintain your current weight of %.1f lbs., you need to eat %.0f calories a day."
						% (Decimal(weightNow), Decimal(round(caloriesMaintain, 0))))

				# a person loses about a pound per week by cutting their maintenance calories by 500
				print("If you wish to lose %.1f lbs. per week, then you should consume %.0f calories a day."
						% (Decimal(weeklyLoss), Decimal(round(caloriesMaintain - (weeklyLoss*500),0))))

			# print help messages
			elif userChoice == 5:
				print("\n" + self.border + "\nAdd New Entry: adds a new log entry to record the date and the user's weight")
				print("Graph Progress: graphs the user's weight progress over a period of time")
				print("Weight Estimator: calculate the user's weight on a given date at their current weight-loss rate (lbs. per week)")
				print("Calorie Tracker:  calculate the calories the user should consume to maintain their current weight, "
					+ "as well as how many calories they should consume to lose a desired amount of weight per week")
				print(self.border + "\n")
				sleep(2)

			# if the user wishes to leave the main menu
			elif userChoice == 6:
				flag = False

			else:
				print("Error: user choice must be one of the numbers above")
