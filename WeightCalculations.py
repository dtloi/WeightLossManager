

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
	if sex.upper() == 'M':
		return main_calculation + 5

	elif sex.upper() == 'F':
		return main_calculation - 161

	else:
		print('Error: sex must be either Male or Female')
		exit()


# return the number of calories the user should consume to remain at their current weight
# weight is in lbs, height is in inches
def CaloricNeeds(sex, age, weight, height, activityLevel, units=('lbs', 'inches')):
	activityLevelMultipliers = {'sedentary': 1.2, 'lightly active': 1.375, 'moderately active': 1.55,
								'hard exercise': 1.725, 'very hard exercise': 1.9}

	return activityLevelMultipliers[activityLevel]*BMR(sex, age, weight, height, units)


if __name__ == '__main__':
	sex = 'Female'
	age = 20
	weight = 56.425
	height = 152.4
	activityLevel = 'sedentary'
	print(BMR(sex, age, weight, height))
	print(CaloricNeeds(sex, age, weight, height, activityLevel))
