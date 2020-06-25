import pyodbc
import re
import WeightCalculations as wc
import GraphWLDB as gwl
from datetime import datetime
from pandas import read_csv


# WeightLoss database manager
class WeightLossDB(object):

	def __init__(self):

		# disallowed characters for usernames in database
		self.userPattern = re.compile("^\.|&|=|_|'|-|\+|,|<|>|\(|\)| ")

		# disallowed characters for passwords in database
		self.passwordPattern = re.compile(" ")

		# connect to SQL Server
		self.connection = None
		try:
			self.connection = pyodbc.connect('Driver={SQL Server};'
							'Server=DESKTOP-NPQM960;'
							'Trusted_Connection=yes;')
			print("Successfully connected to SQL Server!")
		except:
			print("Connection to SQL Server failed!");  exit()

		if self.connection is not None:
			self.connection.autocommit = True

		# place cursor on WeightLoss database
		self.cursor = self.connection.cursor()
		self.cursor.execute("SELECT name FROM master.dbo.sysdatabases where name=?;", ("WeightLoss"))

		data = self.cursor.fetchall()

		# if database already exists
		if data:
			print("Database found successfully.")

		# if database does not already exist, create database and tables
		else:
			print("WeightLoss database does not yet exist....creating...")
			self.cursor.execute("CREATE DATABASE WeightLoss")
			self.cursor.execute("CREATE TABLE Users (uid INTEGER PRIMARY KEY, username varchar(16) NOT NULL UNIQUE, "
				+ "password varbinary(150) NOT NULL, name varchar(25), sex char(1), birthday date, height real, "
				+ "CHECK (sex in ('M', 'F') AND height > 0));")

			self.cursor.execute("CREATE TABLE EntryLogs (uid integer, date date, "
					+ "weight real, PRIMARY KEY (uid, date), FOREIGN KEY (uid) REFERENCES Users ON DELETE CASCADE ON UPDATE CASCADE, "
					+ "CHECK (weight > 0));")


#####################################################################################################################


	# add multiple EntryLogs for previous user from CSV file
	# each line of CSV file must be in form 'uid,date,weight'
	def csvEntryLog(self, filePath, dateFormat="%m/%d/%Y"):
		# get User ID to input CSV data
		uid = None
		username = input("Enter your username: ")
		pwd = input("Enter your password: ")
		data = self.cursor.execute("SELECT uid FROM Users WHERE username=? AND password=HASHBYTES('SHA2_512', ?);",
				(username, pwd)).fetchall()

		# if the query produced a result
		if len(data) != 0:
			uid = int(data[0][0])

		# return False if no query result exists
		else:
			return False

		csv = read_csv(filePath)

		# insert into database
		for index,row in csv.iterrows():
			self.cursor.execute("INSERT INTO EntryLogs(uid, date, weight) VALUES (?,?,?)",
					(uid, datetime.strptime(row['date'], dateFormat), row['weight']))

		return True
