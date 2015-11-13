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
        
    def infer(self,gameState,agentIndex,action):
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
        total=0
        lc=len(cards)
        if lc>0 and table.playable(cards[0]):
            return 1
        if lc>1 and table.playable(cards[1]):
            return 2
        if lc>3 and table.playable(cards[3]):
            return 3
        return 0
    
    def infer(self,gameState,agentIndex,action):
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

class stateAgent(Agent):
    def getAction(self,gameState):
        state=gameState.data.agentState[self.index]
        # play/discard
        for i in reversed(range(len(state.cards))):
            if state.infer[i] is 'playable':
                return ('play',i)
        for i in range(len(state.cards)):
            if state.infer[i] is 'discardable':
                return ('discard',i)
        
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
            if not (state.know[i][0] or state.know[i][1]):
                return ('discard',i)
        for i in range(len(state.cards)):
            if state.infer[i] is not 'dangerous':
                return ('discard',i)
        return ('discard',random.sample(range(len(state.cards)),1)[0])                
    
    def infer(self,gameState,agentIndex,action):
        if not (agentIndex+1)%gameState.rule.numAgent == self.index:
            return
        state=gameState.data.agentState[self.index]
        see=state.peek()
        for i in range(len(state.cards)):
            if state.infer[i] is None and gameState.isDangerous(see[i]):
                state.infer[i]='dangerous'
            if gameState.isPlayable(see[i]):
                state.infer[i]='playable'
            elif gameState.isDiscardable(see[i]):
                state.infer[i]='discardable'
        if (action[0]=='color' or action[0]=='number') and action[1]==self.index:            
            colors, numbers=gameState.getCardStatistics(self.index)
            if action[0]=='number':
                knowCardIndex=numbers[action[2]]
            else:
                knowCardIndex=colors[action[2]]
            first=min(knowCardIndex)
            last=max(knowCardIndex)
            if last==first:
                if state.infer[first] is None:
                    state.infer[first]='playable'
                else:
                    state.infer[first]='dangerous'     
                
### helper functions ###
def groupActions(actions):
    group={'play':[],'discard':[],'color':[],'number':[],'info':[]}
    for a in actions:
        group[a[0]].append(a)
        if a=='color' or a=='number':
            group['info']=[a]
    return group
