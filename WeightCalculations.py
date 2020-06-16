

# calculate Basal Metabolic Rate
# weight is in kg, height is in cm
def BMR(gender, age, weight, height):
	calc = 10*weight + 6.25*height - 5*age
	if gender == 'Male':
		return calc + 5

	elif gender == 'Female':
		return calc - 161

	else:
		print('Error: gender must be either Male or Female')
		exit()



def CaloricNeeds(gender, age, weight, height, activity_level):
	multiplier = 0.0
	if activity_level == 'sedentary':
		multiplier = 1.2
	elif activity_level == 'lightly active':
		multiplier = 1.375
	elif activity_level == 'moderately active':
		multiplier = 1.55
	elif activity_level == 'hard exercise':
		multiplier = 1.725
	elif activity_level == 'very hard exercise':
		multiplier = 1.9
	return multiplier*BMR(gender, age, weight, height)



if __name__ == '__main__':
  # example
	gender = 'Female'
	age = 20
	weight = 56.425
	height = 152.4
	activity_level = 'sedentary'
	print(BMR(gender, age, weight, height))
	print(CaloricNeeds(gender, age, weight, height, activity_level))
