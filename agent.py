import random

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:
    """
    def __init__(self,index):
        self.index=index
    
    def getAction(self, state):
        raiseNotDefined()
        
    def registerInitialState(self, gameState): 
    # inspects the starting state
        return
        
    def inference(self,gameState,agentIndex,action):
    # infer other players' action. Not necessarily implimented in every subclass
        return
         
class randomAgent(Agent):
    def getAction(self,gameState):
        actions=gameState.getLegalActions(self.index)
        group=groupActions(actions)
        if len(group['info'])>0:
            action_type=random.sample(['play','discard','info'],1)[0]
        else:
            action_type=random.sample(['play','discard'],1)[0]
        return random.sample(group[action_type],1)[0]

# only works for numCard=4;
# TODO: generalize to arbitrary numCard (overide parent class init function?)
class informationlessAgent(Agent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        for i in range(len(state.cards)):
            if state.infer[i]:
                return ('play',i)
        total=0
        for i in range(gameState.rule.numAgent):
            if i==self.index:
                continue
            total+=self.checksum(gameState.data.table,gameState.data.agentState[i].cards)
        return ('discard',min((total-1)%4,len(gameState.data.agentState[self.index].cards)))
    
    def checksum(self,table,cards):
        lc=len(cards)
        if lc>0 and table.playable(cards[0]):
            return 1
        if lc>1 and table.playable(cards[1]):
            return 2
        if lc>3 and table.playable(cards[3]):
            return 3
        return 0
    
    def inference(self,gameState,agentIndex,action):
        if agentIndex!=self.index and action[0]=='discard':
            total=action[1]
            subtotal=0
            for i in range(gameState.rule.numAgent):
                if i==self.index or i==agentIndex:
                    continue
                subtotal+=self.checksum(gameState.data.table,gameState.data.agentState[i].cards)
            diff=(total-(subtotal-1))%4
            lc=len(gameState.data.agentState[self.index].cards)
            if lc>0 and diff==1:
                gameState.data.agentState[self.index].infer[0]=True
            if lc>1 and diff==2:
                gameState.data.agentState[self.index].infer[1]=True
            if lc>3 and diff==3:
                gameState.data.agentState[self.index].infer[3]=True
        return

class smartInformationlessAgent(informationlessAgent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        for i in range(len(state.cards)):
            if state.infer[i]:
                return ('play',i)
        index=range(self.index+1,gameState.rule.numAgent)+range(self.index)
        n=[]
        for i in index:
            cks=self.checksum_and_card(gameState.data.table,gameState.data.agentState[i].cards)
            n.append(cks[0])
            if i==index[0]:
                card=cks[1]
            elif n[0]>0 and cks[0]>0 and cks[1]==card: # mutliple agent with the same playable 
                n[0]=0  
        return ('discard',min((sum(n)-1)%4,len(gameState.data.agentState[self.index].cards)))
    
    def checksum_and_card(self,table,cards):
        lc=len(cards)
        if lc>0 and table.playable(cards[0]):
            return (1,cards[0])
        if lc>1 and table.playable(cards[1]):
            return (2,cards[1])
        if lc>3 and table.playable(cards[3]):
            return (3,cards[3])
        return (0,None)

## only works with two players
class informationAgent(smartInformationlessAgent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        for i in range(len(state.cards)):
            if state.infer[i]:
                return ('play',i)
        index=range(self.index+1,gameState.rule.numAgent)+range(self.index)
        n=[]
        for i in index:
            cks=self.checksum_and_card(gameState.data.table,gameState.data.agentState[i].cards)
            n.append(cks[0])
            if i==index[0]:
                card=cks[1]
            elif n[0]>0 and cks[0]>0 and cks[1]==card: # mutliple agent with the same playable 
                n[0]=0
        if gameState.data.clue>0:
            return self.scoreToAction(gameState,self.index,(sum(n)-1)%4)
        else:
            return ('discard',min((sum(n)-1)%4,len(gameState.data.agentState[self.index].cards)))
    
    def scoreToAction(self,gameState,agentIndex,score):
        nextIndex=(agentIndex+score%2+1)%gameState.rule.numAgent        
        if score<2:
            return ('number',nextIndex,gameState.data.agentState[nextIndex].cards[0][1])
        else:
            return ('color',nextIndex,gameState.data.agentState[nextIndex].cards[0][0])
    
    def actionToScore(self,gameState,agentIndex,action):
        score=(action[1]-1-agentIndex)%gameState.rule.numAgent
        if action[0]=='color':
            score += 2
        return score
    
    def inference(self,gameState,agentIndex,action):
        if agentIndex!=self.index:
            if action[0]=='play':
                return
            else:
                if action[0]=='discard':
                    total=action[1]
                else:
                    total=self.actionToScore(gameState,agentIndex,action)
                subtotal=0
                for i in range(gameState.rule.numAgent):
                    if i==self.index or i==agentIndex:
                        continue
                    subtotal+=self.checksum(gameState.data.table,gameState.data.agentState[i].cards)
                diff=(total-(subtotal-1))%4
                lc=len(gameState.data.agentState[self.index].cards)
                if lc>0 and diff==1:
                    gameState.data.agentState[self.index].infer[0]=True
                if lc>1 and diff==2:
                    gameState.data.agentState[self.index].infer[1]=True
                if lc>3 and diff==3:
                    gameState.data.agentState[self.index].infer[3]=True
            return
                
class stateAgent(Agent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        # play/discard
        for i in reversed(range(len(state.cards))):
            if state.infer[i] is 'playable':
                return ('play',i)
        
        # tell next player
        if gameState.data.clue>0:
            nextIndex=(self.index+1)%gameState.rule.numAgent
            nextState=gameState.data.agentState[nextIndex]
            for i in reversed(range(len(nextState.cards))):
                if gameState.isPlayable(nextState.cards[i]):
                    if not nextState.know[i][1]:
                        return ('number',nextIndex,nextState.cards[i][1])
                    if not nextState.know[i][0]:
                        return ('color',nextIndex,nextState.cards[i][0])
            for i in range(len(nextState.cards)):
                if gameState.isDangerous(nextState.cards[i]):
                    if not nextState.know[i][1]:
                        return ('number',nextIndex,nextState.cards[i][1])
                    if not nextState.know[i][0]:
                        return ('color',nextIndex,nextState.cards[i][0])
        
        # random discard
        for i in range(len(state.cards)):
            if state.infer[i] is 'discardable':
                return ('discard',i)
        for i in range(len(state.cards)):
            if not (state.know[i][0] or state.know[i][1]):
                return ('discard',i)
        for i in range(len(state.cards)):
            if state.infer[i] is not 'dangerous':
                return ('discard',i)
        return ('discard',random.sample(range(len(state.cards)),1)[0])                
    
    def inference(self,gameState,agentIndex,action):
        if not (agentIndex+1)%gameState.rule.numAgent == self.index:
            return
        state=gameState.data.agentState[self.index]
        see=state.peek()
        for i in range(len(state.cards)):
            if state.infer[i] is 'playable':
                state.infer[i]=None
            if gameState.isDiscardable(see[i]):
                state.infer[i]='discardable'
            elif gameState.isPlayable(see[i]):
                state.infer[i]='playable'   
            elif gameState.isDangerous(see[i]):
                state.infer[i]='dangerous'
                             
class stateGuessAgent(Agent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        # play/discard
        for i in reversed(range(len(state.cards))):
            if state.infer[i] is 'playable':
                return ('play',i)
        
        # tell next player
        if gameState.data.clue>0:
            nextIndex=(self.index+1)%gameState.rule.numAgent
            nextState=gameState.data.agentState[nextIndex]
            for i in reversed(range(len(nextState.cards))):
                if gameState.isPlayable(nextState.cards[i]):
                    if not nextState.know[i][1]:
                        return ('number',nextIndex,nextState.cards[i][1])
                    if not nextState.know[i][0]:
                        return ('color',nextIndex,nextState.cards[i][0])
            for i in range(len(nextState.cards)):
                if gameState.isDangerous(nextState.cards[i]):
                    if not nextState.know[i][0]:
                        return ('color',nextIndex,nextState.cards[i][0])               
        
        # discard      
        for i in range(len(state.cards)):
            if state.infer[i] is 'discardable':
                return ('discard',i)
        for i in range(len(state.cards)):
            if not (state.know[i][0] or state.know[i][1]):
                return ('discard',i)
        for i in range(len(state.cards)):
            if state.infer[i] is not 'dangerous':
                return ('discard',i)
        return ('discard',random.sample(range(len(state.cards)),1)[0])                
    
    def inference(self,gameState,agentIndex,action):
        if not (agentIndex+1)%gameState.rule.numAgent == self.index:
            return
        state=gameState.data.agentState[self.index]
        see=state.peek()
        for i in range(len(state.cards)):
            if state.infer[i] is 'playable':
                state.infer[i]=None
            if gameState.isDiscardable(see[i]):
                state.infer[i]='discardable'
            elif gameState.isPlayable(see[i]):
                state.infer[i]='playable'   
            elif gameState.isDangerous(see[i]):
                state.infer[i]='dangerous'
                
        if (action[0]=='color' or action[0]=='number') and action[1]==self.index:            
            colors, numbers=gameState.getCardStatistics(self.index)
            if action[0]=='number':
                knowCardIndex=numbers[action[2]]
            else:
                knowCardIndex=colors[action[2]]
            first=min(knowCardIndex)
            last=max(knowCardIndex)
            if last==first:
                if action[0]=='color' and not state.know[first][0]: # knows only color
                    state.infer[first]='dangerous'
                elif action[0]=='number':
                    state.infer[first]='playable'
            if action[0]=='number':
                state.infer[last]='playable'
            elif state.know[last][1]:
                state.infer[last]='playable'
            else:
                state.infer[first]='dangerous'
                    
class oracleAgent(Agent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        # play/discard
        for i in reversed(range(len(state.cards))):
            if state.infer[i] is 'playable':
                return ('play',i)
                
        # tell next player
        if gameState.data.clue>0:
            nextIndex=(self.index+1)%gameState.rule.numAgent
            nextState=gameState.data.agentState[nextIndex]
            return ('number',nextIndex,nextState.cards[0][1])
                       
        for i in range(len(state.cards)):
            if state.infer[i] is 'discardable':
                return ('discard',i)
        for i in range(len(state.cards)):
            if state.infer[i] is not 'dangerous':
                return ('discard',i)
                
        # random discard
        return ('discard',random.sample(range(len(state.cards)),1)[0])                
    
    def inference(self,gameState,agentIndex,action):
        if not (agentIndex+1)%gameState.rule.numAgent == self.index:
            return
        state=gameState.data.agentState[self.index]
        see=state.cards
        for i in range(len(state.cards)):
            if state.infer[i] is None or state.infer[i] is 'dangerous':
                if gameState.isDangerous(see[i]):
                    state.infer[i]='dangerous'
                if gameState.isPlayable(see[i]):
                    state.infer[i]='playable'
                elif gameState.isDiscardable(see[i]):
                    state.infer[i]='discardable'
                    
class MaxMaxAgent(Agent):
    #similar to minimax, but here is a collaboration game:
    def __init__(self,index):
        self.index=index
        self.depth=2
    
    def evaluationFunction(self, gameState):
        utility=gameState.getScore()
        myTrash=gameState.data.trash.state
        for card in myTrash:
            color,number=card
            if myTrash[card]==gameState.rule.numNumber[number]:
                utility-=100
        utility+=gameState.data.clue
        return utility

    def getAction(self, gameState):
        optimalActions=[]
        def recComputeVopt(gameState, depth, agentIndex):
            Actions=gameState.getLegalActions(agentIndex)
            if gameState.isEnd() or (not Actions):
                return gameState.getScore()
            if depth==0:
                return self.evaluationFunction(gameState)
            if agentIndex < gameState.getNumAgents()-1:
                values=[recComputeVopt(gameState.generateSuccessor(agentIndex, a), depth, agentIndex+1) for a in Actions]
            else:
                values=[recComputeVopt(gameState.generateSuccessor(agentIndex, a), depth-1, 0) for a in Actions]
            optimalValue=max(values)
            if agentIndex==self.index and depth==self.depth:
                for i, v in enumerate(values):
                    if v==optimalValue:
                        optimalActions.append(Actions[i])
        _=recComputeVopt(gameState, self.depth, self.index)
        return random.choice(optimalActions)

### helper functions ###
def groupActions(actions):
    group={'play':[],'discard':[],'color':[],'number':[],'info':[]}
    for a in actions:
        group[a[0]].append(a)
        if a=='color' or a=='number':
            group['info']=[a]
    return group
