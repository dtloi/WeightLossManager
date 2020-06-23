# WeightLossManager
A weight loss progress tracker, using SQL injections in Python.

### WeightLossDB.py:
Handles basic access to the WeightLoss database. Add a new user or add entry logs for a previous user. Reads data from a CSV file when given the filepath.

### WeightLossUI.py:
Runs a command-line User Interface so a user can interact with and update the database without using CSV files.

### WeightCalculations.py:
Performs supplementary calculations to find the user's BMR (Basal Metabolic Rate) and recommended calorie intake for a desired weight-loss plan.

### GraphWLDB.py:
Creates visualization of the user's weight-loss progress over a period of time.


## User Interface Tutorial
In order to start the UI, one must simply run the RunManager.py file with no command-line arguments for Click.
![Startup Menu](/images/startup.png)
