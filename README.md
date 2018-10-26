# NBA Wins Pool Flask App 

### Table of Contents
- [Project Description](#project-description)
- [Data](#data)
- [Roadmap](#roadmap)
- [Development](#development)
- [Predictions](#predictions)
- [Authors](#authors)

## Project Description
A flask app that outputs the total amount of wins for each player in the NBA. The Wins Pool made popular by Bill Simmons, is a draft with 10 players where:

	* Each players drafts three NBA teams. The player with the most combined wins is the champion.

	* The draft isn’t a snake format but instead a unique drafting system that looks like this:

		* Team 1 — 1st pick, 20th pick, 26th pick

		* Team 2 — 2, 16, 29

		* Team 3 — 3, 13, 30

		* Team 4 — 4, 18, 25

		* Team 5 — 5, 15, 27
		
		* Team 6 — 6, 19, 22

		* Team 7 — 7, 11, 28

		* Team 8 — 8, 17, 21

		* Team 9 — 9, 14, 23

		* Team 10 — 10, 12, 24

This app outputs live stats from data.nba.net so the user can know where they stand day by day. Additionally there is a machine learning algorithm that predicts the future signal of wins for each team, and a 95% confidence interval of wins for each player at the end of the season. The data used to train is historical standings throughout the season since the 2014-15 NBA season. 

## Data
Data comes from data.nba.net

More info to write here...

## Roadmap
* Add websockets to show live games and stats without refreshing
* Refine model for predicting win signal and final points
* Create a user management system to allow for other leagues

## Development
The flask app is run on docker. All you have to do is download docker and then run this within the project directory to run locally.
```shell
source run_docker.sh
```
## Predictions
More info to write here on algorithm and how it works. Add a rest API for others to use 

## Authors
- Chris Vela (info@christophvel.com)