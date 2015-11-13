from game import *

agents=[]
'''
for i in range(2):
    agents.append(MaxMaxAgent(i))
    #agents.append(informationlessAgent(i))
game=Game(agents, 1, [2,1],numCard=1,numClue=7)
'''

for i in range(3):
    #agents.append(oracleAgent(i))
    #agents.append(randomAgent(i))
    #agents.append(informationlessAgent(i))
    #agents.append(smartInformationlessAgent(i))
    agents.append(stateAgent(i))
    
result=[]
NMC=1
for i in range(NMC):
    game=Game(agents)
    result.append(game.run(1))
print ", ".join(map(str,result))
