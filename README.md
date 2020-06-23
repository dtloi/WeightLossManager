# WeightLossManager
A weight loss progress tracker, using SQL injections in Python. My primary motivation for this project was to teach myself the basics of database management while applying it to a programming language I was already quite comfortable using. Updates and additional features will be added over time.

###<ins>File Descriptions</ins>
#### WeightLossDB.py:
Handles basic access to the WeightLoss database. Add a new user or add entry logs for a previous user. Reads data from a CSV file when given the filepath.

#### WeightLossUI.py:
Runs a command-line User Interface so a user can interact with and update the database without using CSV files.

#### WeightCalculations.py:
Performs supplementary calculations to find the user's BMR (Basal Metabolic Rate) and recommended calorie intake for a desired weight-loss plan.

#### GraphWLDB.py:
Creates visualization of the user's weight-loss progress over a period of time.


## User Interface Tutorial
In order to start the UI, one must simply run the RunManager.py file with no command-line arguments for Click. In order to interact with the menu, the user must simply type the number next to their desired option.
![Startup Menu](/images/startup.png)

If it is the user's first time using the program, they can enter their information under the New User option
![New User](/images/newuser0.png)


They will then be prompted to enter their first entry, logging their weight and the date.
![new entry](/images/newentry.png)

It is also possible to bypass the UI and enter new user or log entry data directly via CSV files. Simply include the filepath in the appropriate Click option and run the startup file.
![csv_entry](/images/csventry.png)

If one does not know their UserID (UID), then they can also search the database by name
![namelookup](/images/namelookup1.png)

All relevant results will be displayed so they can find their login information
![namelookup2](/images/namelookup2.png)

Once the user has identified themself, they now move to the main menu, where they have a variety of options to choose from
![mainmenu](/images/mainmenu.png)

The user has the option to graph their progress over a set course of months
![graph](/images/graph.png)

The user can also get their predicted weight on a given day using a weightloss schedule (lbs. lost per week)
![weightestimator](/images/weightestimator.png)
