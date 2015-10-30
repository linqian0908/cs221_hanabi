class GameState:
    def __init__(self,rule,data):
        self.data=data
        self.rule=rule
    
    def getCardStatistics(self,agentIndex):
        infoCards=self.data.agentState[agentIndex].cards
        colors={}
        numbers={}
        for i in range(len(infoCards)):
            if infoCards[i][0] in colors:
                colors[infoCards[i][0]].append(i)
            else:
                colors[infoCards[i][0]]=[i]
            if infoCards[i][1] in numbers:
                numbers[infoCards[i][1]].append(i)
            else:
                numbers[infoCards[i][1]]=[i]
        return (colors, numbers)
    

    def getLegalActions(self,agentIndex):
        # return [('play',#),('discard', #),('color', player#, #) ('number', player#, #)]
        LegalActions=[]
        if self.isEnd():
            return LegalActions
        for i in range(len(self.data.agentState[agentIndex].cards)):
            LegalActions.append(('play', i))
            LegalActions.append(('discard', i))
        if self.data.clue>0:
            numAgents=self.getNumAgents()
            for i in range(1, numAgents):
                colors,numbers=self.getCardStatistics((agentIndex+i)%numAgents)
                for color in colors:
                    LegalActions.append(('color', (agentIndex+i)%numAgents, color))
                for number in numbers:
                    LegalActions.append(('number', (agentIndex+i)%numAgents, number))
        return LegalActions
            
    def generateSuccessor(self,agentIndex, action):
        if self.isEnd(): raise Exception('Can\'t generate a successor of a terminal state.')
        state = GameState(self.rule, self.data)
        if action[0]=='play':
            card=state.data.agentState[agentIndex].pop(action[1])
            isValid=state.data.table.add(card)
            if not isValid:
                state.data.trash.add(card)
                if state.data.clue>0:
                    state.data.clue-=1
            if state.data.additionalTerms==float('inf'):
                newcard=state.data.deck.draw()
                if newcard!=None:
                    state.data.agentState[agentIndex].add(newcard)
                else:
                    state.data.additionalTerms=state.getNumAgents()
            else:
                state.data.additionalTerms-=1
        elif action[0]=='discard':
            if state.data.clue<state.rule.numClue:
                state.data.clue+=1
            card=state.data.agentState[agentIndex].pop(action[1])
            state.data.trash.add(card)
            if state.data.additionalTerms==float('inf'):
                newcard=state.data.deck.draw()
                if newcard!=None:
                    state.data.agentState[agentIndex].add(newcard)
                else:
                    state.data.additionalTerms=state.getNumAgents()
            else:
                state.data.additionalTerms-=1
        else:
            state.data.clue-=1
            AgentReceivInfo=state.data.agentState[action[1]]
            colors, numbers=self.getCardStatistics(action[1])
            if action[0]=='color':
                knownCardsIndex=colors[action[2]]
                for i in knownCardsIndex:
                    AgentReceivInfo.know[i]=('True',AgentReceivInfo.know[i][1])
            if action[0]=='number':
                knownCardsIndex=numbers[action[2]]
                for i in knownCardsIndex:
                    AgentReceivInfo.know[i]=(AgentReceivInfo.know[i][0],'True')
            if state.data.additionalTerms!=float('inf'):
                state.data.additionalTerms-=1
        return state

    def getNumAgents(self):
        return self.rule.numAgent

    def getScore(self):
        finalScore=self.data.table.getScore()
        if self.isWin():
            finalScore+=10000
        return finalScore

    def isEnd(self):
        return self.data.additionalTerms<=0 or self.isWin()
    
    def isWin(self):
        return self.data.table.getScore()==self.rule.numColor*len(self.rule.numNumber)
    
    def deepCopy(self):
        return GameState(self.rule,self.data.deepCopy())
    
    def isDangerous(self,card):
        if self.data.table.check(card):
            return False
        color,number=card
        return self.data.trash.check(card)>=self.rule.numNumber[number]
