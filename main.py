#IMPORTS

import sys
import random
import numpy as np
import matplotlib
matplotlib.use('QT4Agg')
import matplotlib.pyplot as plt

################################################################

#SELECTION OF GAME TO BE PLAYED

#STAG HUNT
alpha = .5
payoff = [
	[1+alpha,0],
	[1,1]
]
#SET UP PURE COORDINATION "BATTLE OF THE SEXES"
Npayoff = [
	[1,0],
	[0,1]
]
#PRISONER'S DILLEMMA
Npayoff = [
	[-1,-3],
	[0,-2]
]
#PURE DISCOORDINATION
Npayoff = [
	[0,1],
	[1,0]
]

################################################################

#CREATE THE PLAYER "CLASS"
class Player:
	def __init__(self,strategy):
		self.strategy = strategy
		self.moveThisTurn = 0
		self.history = []

################################################################

#OPEN DATA, CLEAN IT, AND INSTANTIATE PLAYER OBJECTS.

#settings
#stag = 1 # ALWAYS CHOOSE A
#hare = 2 # ALWAYS CHOOSE B
#GRIM = 3 # ALWAYS CHOOSE A, UNTIL B SHOWS IN YOUR HISTORY
#learner = 4
#random = 5

f=open('data.txt','r+')
dat = f.readlines()

newDat = []
for i in dat:
	i = i.strip().split()
	newDat.append(i)

matrix = []
xPos = 0
for i in newDat:
	line = []
	for j in i:
		if j == '0':
			line.append(0)
		else:
			line.append(Player(int(j)))
			
	matrix.append(line)

''' #BACKUP!
matrix  = [
	[1,1,1,1,1],
	[1,Player(stag),Player(stag),Player(stag),1],
	[1,Player(stag),Player(stag),Player(stag),1],
	[1,Player(stag),Player(stag),Player(stag),1],
	[1,1,1,1,1]
] #SIMPLE 3x3 GRID'''

################################################################

#TURN BEGINS. THIS IS WHERE THE LOOP ALSO BEGINS.

def runTurn(turnNumber):

	#ESTABLISHES A MASTER LIST OF UNIQUE INTERACTIONS TO CONDUCT THIS TURN
	interactionsList = []

	#returns list of possible interactions
	def findInteractions(xPos,yPos):
		#print(type(matrix[xPos][yPos]))

		#IF NOT PLAYER, DO NOTHING.
		if type(matrix[xPos][yPos]).__name__ == 'int':
			return

		#ADD IT TO THE LIST OF ELIGIBLE INTERACTIONS, IF IT IS A "VALID" INTERACTION.

		#TEST UPPER RIGHT
		if type(matrix[xPos-1][yPos+1]).__name__ != 'int':
			interactionsList.append([matrix[xPos][yPos],matrix[xPos-1][yPos+1]])

		#TEST RIGHT
		if type(matrix[xPos][yPos+1]).__name__ != 'int':
			interactionsList.append([matrix[xPos][yPos],matrix[xPos][yPos+1]])	
		
		#TEST LOWER RIGHT
		if type(matrix[xPos+1][yPos+1]).__name__ != 'int':
			interactionsList.append([matrix[xPos][yPos],matrix[xPos+1][yPos+1]])
		
		#TEST DIRECTLY BELOW
		if type(matrix[xPos+1][yPos]).__name__ != 'int':
			interactionsList.append([matrix[xPos][yPos],matrix[xPos+1][yPos]])

	for i in range(len(matrix)):
		for j in range(len(matrix[i])):
			findInteractions(i,j)

	################################################################

	#WHAT WILL EACH PLAYER DO? WILL ACT RANDOMLY,BASED ON THEIR OWN MIXED STRATEGY.

	#SET THEIR MIXED STRATEGY
	def calculateBestResponse(player):

		#TAKE HISTORY, GET RANDOM SELECTION 

		if len(player.history) < 3:
			#always cooperate if you've done only 1 or 2 interactions.
			return 1
		

		#need to calculate average based on history
		#this is where you can take a random sample
		if len(player.history) > 8: #MINIMUM SAMPLE SIZE BEFORE CUTTING SOME VALUES OUT.
			sampleHistory = random.sample(player.history, 6) # SECOND NUMBER IS NUMBER OF SAMPLES WE WANT TO TAKE, i.e, 8.
		else:
			sampleHistory = player.history

		#TODO: It would be easy to extend this and weight more recent interactions. That's something for another time ;)
		#print("It is turn number",turnNumber)
		#print(sampleHistory)

		avgTotalConf = 0
		for historicalConflict in sampleHistory: # for each conflict in recent history (n < 10)
			avgTotalConf = avgTotalConf + historicalConflict # add to the total
		avgConf = float(avgTotalConf) / float(len(sampleHistory)) # then divide by # of interactions polled.
		oppStrat = avgConf

		#print("Opponent Strategy is ",oppStrat,sampleHistory)

		#MAXIMIZE EXPECTED PAYOFF, MULTIPLY BY YOUR OPPONNENTS' EXPECTED DECISIONS.
		x = 0
		lowerBound = (payoff[0][0] * oppStrat * x) + (payoff[0][1] * (1-oppStrat) * x) + (payoff[1][0] * oppStrat * (1-x)) + (payoff[1][1] * (1-oppStrat) * (1-x))
		x = 1
		upperBound = (payoff[0][0] * oppStrat * x) + (payoff[0][1] * (1-oppStrat) * x) + (payoff[1][0] * oppStrat * (1-x)) + (payoff[1][1] * (1-oppStrat) * (1-x))

		#NOTE: THIS ONLY WORKS FOR LINEAR PAYOFFS. HOWEVER, BASIN OF ATTRACTION FOR MIXED STRATEGY DOESN'T SEEM TO EXIST.
		if (lowerBound > upperBound):
			return 0
		else:
			return 1

	print(len(matrix))
	#FOR EACH PLAYER FIND PROBABILITY OF SELECTING FIRST OPTION.
	for i in matrix: # for each line
		for j in i:
			if type(j).__name__ == 'instance':
				if j.strategy == 1: #STAG
					j.moveThisTurn = 1
				elif j.strategy == 2: #HARE
					j.moveThisTurn = 0
				elif j.strategy == 3: #GRIM
					j.moveThisTurn = 1
				elif j.strategy == 4: #LEARNER
					j.moveThisTurn = calculateBestResponse(j)
				elif j.strategy == 5: #random
					chanceOfA = random.random()
					j.moveThisTurn = np.random.choice([1,0],1,p=[chanceOfA,1-chanceOfA])
		#print("New Line")

	#ITERATE THROUGH INTERACTIONS AND ADD TO HISTORIES

	'''this is complex. It checks if the player is a learner, 
	collects all of the player's interactions, 
	records their outcome, and appends it to the player's history'''

	for i in matrix:
		for j in i:
			if type(j).__name__ == 'instance':
				#print(j.moveThisTurn)
				if j.strategy == 4: #player is a learner
					interactionsWithPlayer = []
					for turn in interactionsList: #iterate through all the interactions
						if j in turn:
							#print("found interaction!")
							#print(turn)
							#get other player's name
							for playerInTurn in turn:
								if playerInTurn != j:
									interactionsWithPlayer.append(playerInTurn.moveThisTurn)
					#print(interactionsWithPlayer) #THESE PLAYERS HAD AN INTERACTION WITH THIS PLAYER
					avgTotal = 0
					for interactions in interactionsWithPlayer: #FIND AVERAGE OF THESE INTERACTIONS
						avgTotal = avgTotal + interactions
					average = (float(avgTotal) / float(len(interactionsWithPlayer))) 
					j.history.append(average) #add average to the history of that specific player. 
					#if len(j.history) > 10:
					#	#del(j.history[0]) #this creates a "rolling" average. if the history gets too long, delete the first value to keep it at 10.
					#	pass
	#if you're GRIM, change strategy to always choose option B if any opponnent ever cheats.
	#if you're GRIM with forgivenss, change strategy to go B for N turns.
	#if you're TIT-FOR-TAT, do what other player did previously.

	#GRIM DETECTOR
	for i in matrix:
		for j in i:
			if type(j).__name__ == 'instance':
				#print(j.moveThisTurn)
				if j.strategy == 3: #player is GRIM
					interactionsWithPlayer = []
					for turn in interactionsList: #iterate through all the interactions
						if j in turn:
							for playerInTurn in turn:
								if playerInTurn != j:
									if playerInTurn.moveThisTurn == 0:
										j.strategy = 2 # always choose B
				

	########################################################

	#GET STRATEGY MATRIX (WHAT STRATEGY IS THE PLAYER USING?)
	def getStrategyMatrix():
		strategyMatrix = []
		for i in matrix:
			line = []
			for j in i:
				if type(j).__name__ == 'int':
					line.append(0)
				else:
					line.append(j.strategy)
			strategyMatrix.append(line)
		return strategyMatrix

	#GET DECISION MATRIX (WHAT ACTUAL MOVE IS BEING PLAYED?)
	def getDecisionMatrix():
		decisionMatrix = []
		for i in matrix:
			line = []
			for j in i:
				if type(j).__name__ == 'int':
					line.append(0.5)
				else:
					line.append(j.moveThisTurn)
			decisionMatrix.append(line)
		return decisionMatrix

	#DISPLAY MATRICES
	def generateFigure(strategyMatrix,playerDecisionMatrix):
		min_val, max_val = 0, 15
		fig, ax = plt.subplots()
		#intersection_matrix = np.random.randint(0, 10, size=(max_val, max_val))

		ax.matshow(playerDecisionMatrix, cmap=plt.cm.Blues)

		for i in xrange(15):
		    for j in xrange(15):
		        c = strategyMatrix[j][i]
		        ax.text(i, j, str(c), va='center', ha='center')
		ax.set_xlim(min_val-1, max_val)
		ax.set_ylim(max_val,min_val-1)
		ax.set_xticks(np.arange(max_val))
		ax.set_yticks(np.arange(max_val))

		figure = plt.figure(figsize=(30, 30), dpi=300)
		fig.savefig(r"output\\chart" + str(turnNumber) + ".png")

	strategyMatrix = getStrategyMatrix()
	#print(strategyMatrix)
	playerDecisionMatrix = getDecisionMatrix()
	#print(playerDecisionMatrix)
	generateFigure(strategyMatrix,playerDecisionMatrix)

for turnNumber in range(30):
	runTurn(turnNumber)