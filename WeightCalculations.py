import pyodbc
import WeightCalculations as wc
import GraphWLDB as gwl
from datetime import date, datetime
from pandas import read_csv, read_sql_query


# WeightLoss database manager
class WeightLossDB(object):

	####################################################################################################
	### init
	def __init__(self):

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
			self.cursor.execute("CREATE TABLE Users (uid INTEGER PRIMARY KEY, name varchar(25), sex CHAR(1), "
					+ "birthday date, height real, CHECK (sex in ('M', 'F') AND height > 0));")

			self.cursor.execute("CREATE TABLE EntryLogs (lid INTEGER PRIMARY KEY, uid integer, date date, "
					+ "weight real, FOREIGN KEY (uid) REFERENCES Users ON DELETE CASCADE ON UPDATE CASCADE, "
					+ "CHECK (weight > 0));")

	### end init
	####################################################################################################

	# add multiple new users from CSV file (without using User Interface)
	# each line of CSV file must be in form 'name,sex,birthday,height'
	def newUser(self, filePath, dateFormat="%m/%d/%Y"):
		data = read_csv(filePath)
		for index,row in data.iterrows():
			lastIndex = self.cursor.execute("SELECT MAX(uid) FROM Users;").fetchall()[0][0]
			uid = int(lastIndex) + 1 if lastIndex is not None else 1
			self.cursor.execute("INSERT INTO Users(uid,name,sex,birthday,height) VALUES (?,?,?,?,?)",
					(uid, row['name'], row['sex'], datetime.strptime(row['birthday'], dateFormat), row['height']))



	# add multiple EntryLogs *for previous users* from CSV file (without using User Interface)
	# each line of CSV file must be in form 'uid,date,weight'
	def addEntryLog(self, filePath, dateFormat="%m/%d/%Y"):
		data = read_csv(filePath)
		for index,row in data.iterrows():
			lastIndex = self.cursor.execute("SELECT MAX(lid) FROM EntryLogs;").fetchall()[0][0]
			lid = int(lastIndex) + 1 if lastIndex is not None else 1
			self.cursor.execute("INSERT INTO EntryLogs(lid, uid, date, weight) VALUES (?,?,?,?)",
					(lid, row['uid'], datetime.strptime(row['date'], dateFormat), row['weight']))
