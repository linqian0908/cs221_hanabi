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
    The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
    must return an action from Directions.{North, South, East, West, Stop}
    """
    raiseNotDefined()
    
class randomAgent(Agent):
    def getAction(self,gameState):
        actions=gameState.getLegalActions(self.index)
        return random.sample(actions,1)[0]
        

class MaxMaxAgent(Agent):
    #similar to minimax, but here is a collaboration game:
    def evaluationFunction(self, gameState):
        return gameState.getScore()
    def getAction(self, gameState):
        optimalActions=[]
        def recComputeVopt(gameState, depth, agentIndex):
            Actions=gameState.getLegalActions(agentIndex)
            if gameState.isEnd() or (not Actions):
                return gameState.getScore()
            if depth==0:
                return self.evaluationFunction(gameState)
            if agentIndex<gameState.getNumAgents()-1:
                values=[recComputeVopt(gameState.generateSuccessor(agentIndex, a), depth, agentIndex+1) for a in Actions]
            else:
                values=[recComputeVopt(gameState.generateSuccessor(agentIndex, a), depth-1, 0) for a in Actions]
            optimalValue=max(values)
            if agentIndex==self.index and depth==self.depth:
                for i, v in enumerate(values):
                    if v==optimalValue:
                        optimalActions.append(Actions[i])
            return optimalValue
        _=recComputeVopt(gameState, 1, self.index)
        return random.choice(optimalActions)

