import random

class Agent:
  """
  An agent must define a getAction method, but may also define the
  following methods which will be called if they exist:

  def registerInitialState(self, state): # inspects the starting state
  """
  def __init__(self,index):
    self.index=index
    
  def getAction(self, state):
    """
    The Agent will receive a GameState and must return an action
    """
    raiseNotDefined()
    
class randomAgent(Agent):
    def getAction(self,gameState):
        actions=gameState.getLegalActions(self.index)
        return random.sample(actions,1)[0]
    
    def infer(self,gameState,agentIndex,action):
        return

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
            
class panicAgent(Agent):
    # assume agent use the following strategy (known to each other)
    # if clue>0: check next player's card of no info and is dangerous (from oldest)
    # infer playable card and play (simple infer, using table, trash and other agent's card)
    # discard oldest informationless card
    # random info
    # random play/discard
    def tell(self,gameState,agentIndex):
        state=gameState.data.agentState(agentIndex)
        cards=state.cards
        know=state.know
        for i in range(len(cards)):
            if not know[i][0]|know[i][1]:
                if gameState.isDangerous(cards[i]):
                    return i
        return -1
    
    def getAction(self,gameState):
        actions=gameState.getLegalAction(self.index)
        group=groupActions(actions)
        nextIndex=(self.index+1) % gameState.rule.numAgent
        # tell dangerous card
        if gameState.data.clue>0:
            cardIndex=tell(gameState,nextIndex)
            if cardIndex>-1:
                for actcolor,agent,cardcolor in group['color']:
                    if agent==nextIndex and cardIndex in cardcolor:
                        break
                for actnum,agent,cardnum in group['number']:
                    if agent==nextIndex and cardIndex in cardnum:
                        break
                if sum(cardcolor)<sum(cardnum):
                    return ('color',nextIndex,cardcolor)
                if sum(cardnum)<sum(cardcolor):
                    return ('number',nextIndex,cardnum)
                return random.sample([('color',nextIndex,cardcolor),('number',nextIndex,cardnum)],1)[0]
        # infer playable card
        
    def inter(self,gameState,agentIndex,action):
        return
                                  
### helper functions ###
def groupActions(actions):
    group={'play':[],'discard':[],'color':[],'number':[]}
    for a in actions:
        group[a[0]].append(a)
    return group
