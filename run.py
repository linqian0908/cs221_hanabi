from game import *

agents=[]
'''
for i in range(2):
    agents.append(MaxMaxAgent(i))
    #agents.append(informationlessAgent(i))
game=Game(agents, 1, [2,1],numCard=1,numClue=7)
'''

for i in range(3):
    #agents.append(stateAgent(i))
    #agents.append(informationlessAgent(i))
    #agents.append(randomAgent(i))
    agents.append(oracleAgent(i))
result=[]
NMC=100
for i in range(NMC):
    game=Game(agents)
    result.append(game.run(0))
print ", ".join(map(str,result))
