from datetime import datetime
# a collection of helper methods for WeightLoss Manager that perform calculations involving weight


# get the estimated number of lbs lost between today and the given date with the given number of lbs lost per week
def lbsLost(date, lbsLoss, dateFormat="%m/%d/%Y"):
	now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	later = datetime.strptime(date, dateFormat)
	days = (later - now).days

	# x lbs per week is equal to x/7 lbs per day
	return days*(lbsLoss/7)



# calculate the user's Basal Metabolic Rate
# default weight is in lbs, default height is in inches
def BMR(sex, age, weight, height, units=('lbs', 'inches')):

	# if weight in pounds, convert to kg
	if units[0] == 'lbs':
		weight *= 0.453592

	elif units[0] != 'kg':
		print("Error: weight must be in either lbs or kg");  exit()

	# convert inches to centimeters
	if units[1] == 'inches':
		height *= 2.54

	elif units[1] != 'cm':
		print("Error: height must be in either inches or cm");  exit()

	main_calculation = 10*weight + 6.25*height - 5*age

	# the sex of the user creates either a bonus or decrease to the permitted-calorie calculation
	sexID = sex.upper()
	if sexID == "M" or sexID == "MALE":
		return main_calculation + 5

	elif sexID == "F" or sexID == "FEMALE":
		return main_calculation - 161

	else:
		print('Error: sex must be either Male or Female');  exit()



# return the number of calories the user should consume to remain at their current weight
# weight is in lbs, height is in inches
def CaloricNeeds(sex, age, weight, height, activityLevel, units=('lbs', 'inches')):
	activityLevelMultipliers = {'sedentary': 1.2, 'lightly active': 1.375, 'moderately active': 1.55,
								'hard exercise': 1.725, 'very hard exercise': 1.9}

	return activityLevelMultipliers[activityLevel]*BMR(sex, age, weight, height, units)



# testing
if __name__ == '__main__':
	sex = 'Male'
	age = 26
	weight = 240
	height = 73
	activityLevel = 'sedentary'
	print(BMR(sex, age, weight, height))
	print(CaloricNeeds(sex, age, weight, height, activityLevel))
	print(lbsLost("07/6/2020", 2))
