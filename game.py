from collections import Counter
import copy
import random
from gameState import *
from agent import *

class AgentState:
    def __init__(self,cards,know=None,infer=None):
        self.cards=cards
        if know is None:
            self.know=[(False,False)]*len(self.cards)
        else:
            self.know=know
        if infer is None:
            self.infer=[None]*len(self.cards)
        else:
            self.infer=infer
        
    def pop(self,i):
    # remove the i-th card from the hand
        if i<len(self.cards):
            self.know.pop(i)
            self.infer.pop(i)
            return self.cards.pop(i)
        return None
        
    def add(self,card):
    # add a card to the last on hand
        self.cards.append(card)
        self.know.append((False,False))
        self.infer.append(None)
    
    def peek(self):
        see=[]
        for i in range(len(self.cards)):
            if self.know[i][0]:
                if self.know[i][1]:
                    see.append(self.cards[i])
                else:
                    see.append((self.cards[i][0],-1))
            else:
                if self.know[i][1]:
                    see.append((-1,self.cards[i][1]))
                else:
                    see.append((-1,-1))
        return see
        
    def copy(self):
        return AgentState(copy.deepcopy(self.cards),copy.deepcopy(self.know),copy.deepcopy(self.infer))
        
class Deck:
    def __init__(self,prev=None):
        if prev!=None:
            self.state=prev.state
                    
    def initialize(self,numColor,numNumber):
        self.state={}
        for i in range(numColor):
            for j in range(len(numNumber)):
                self.state[(i,j)]=numNumber[j]
        self.state=Counter(self.state)
        return
        
    def draw(self):
    # randomly draw a card from hand. return: (color,number); None if no card in deck
        if sum(self.state.values())<1:
            return None
        card=random.sample(list(self.state.elements()),1)[0]
        self.state[card]-=1
        return card
   
    def deepCopy(self):
        copied=Deck();
        copied.state=copy.deepcopy(self.state)
        return copied
        
class Table:
    def __init__(self,prev=None):
        if prev!=None:
            self.state=prev.state
    
    def initialize(self,numColor):
        self.state=[-1]*numColor
        return
    
    def add(self,card):
    # attemp to add card to table. return: True if success (legal move); False o.w.
        color,number=card
        if self.state[color]==number-1:
            self.state[color]+=1
            return True
        return False
    
    def playable(self,card):
        color,number=card
        if color>=0 and number>=0: # know both information
            return self.state[color]==number-1
        return False # know only color
            
    def check(self,card):
    # check if a card is already played. return: True if is played
        color,number=card
        if color>=0 and number>=0: # know both information
            return self.state[color]>=number
        return False
        
    def getScore(self):
        return sum(self.state)+len(self.state)
    
    def deepCopy(self):
        copied=Table();
        copied.state=copy.deepcopy(self.state)
        return copied
        
class Trash:
    def __init__(self,state=None):
        if state!=None:
            self.state=state
        else:
            self.state=Counter()
    
    def add(self,card):
    # add a card to trash
        self.state[card]+=1
        return
    
    def check(self,card):
    # return number of a certain type of card is in trash
        color,number=card
        if color>=0 and number>=0:
            return self.state[card]
        return -1
    
    def deepCopy(self):
        return Trash(copy.deepcopy(self.state))
        
class GameStateData:
    def __init__(self,prev=None):
        if prev!=None:
            self.deck=prev.deck
            self.clue=prev.clue
            self.table=prev.table
            self.trash=prev.trash
            self.agentState=self.copyAgentStates(prev.agentState)
            self.additionalTerms=prev.additionalTerms
    
    def initialize(self,rule):
        self.deck=Deck()
        self.deck.initialize(rule.numColor,rule.numNumber)
        self.clue=rule.numClue;
        self.table=Table()
        self.table.initialize(rule.numColor)
        self.trash=Trash()
        
        self.agentState=[None]*rule.numAgent
        for i in range(rule.numAgent):
            cards=[None]*rule.numCard
            for j in range(rule.numCard):
                cards[j]=self.deck.draw()
            self.agentState[i]=AgentState(cards) # may need to deep copy
        self.additionalTerms=float('inf')
    
    def deepCopy(self):
        state=GameStateData(self)
        state.deck=self.deck.deepCopy()
        state.table=self.table.deepCopy()
        state.trash=self.trash.deepCopy()
        return state
        
    def copyAgentStates(self,agentState):
        copied=[]
        for state in agentState:
            copied.append(state.copy())
        return copied
         
class Rule:
    def __init__(self,numColor,numNumber,numCard,numClue,numAgent):
        self.numColor=numColor #total number of color
        self.numNumber=numNumber #array of multiplicity of each number
        self.numCard=numCard #number of cards on hand
        self.numClue=numClue #number of clue
        self.numAgent=numAgent #number of agent
               
class Game:
    def __init__(self,agents,numColor=5,numNumber=[3,2,2,2,1],numCard=4,numClue=7):
        self.rule=Rule(numColor,numNumber,numCard,numClue,len(agents))
        self.gameOver=False
        initstate=GameStateData()
        initstate.initialize(self.rule)
        self.state=GameState(self.rule,initstate)
        self.agentList=[]
        for i in range(len(agents)):
            self.agentList.append(agents[i])
            agents[i].registerInitialState(self.state)
    
    def finish(self,verbose=0):
        if verbose:
            if self.state.isWin():
                print "Win!"
            else:
                print "Lose~"
            print "finish with score ",self.state.getScore()
        return self.state.getScore()
        # TODO: print out table and trash
        
    def run(self, verbose=0):
        agentIndex=0
        
        while not self.gameOver:
            # fetch the next agent
            # Generate an observation of the state
            observation=self.state.deepCopy()
            # Solicit an action
            if verbose:
                observation.printData()
            agent=self.agentList[agentIndex]
            action = agent.getAction(observation)
            if verbose:
                print "#### Now the player ", agent.index, " takes action: ", action
            # Execute the action
            self.state=self.state.generateSuccessor(agentIndex,action)
            for a in self.agentList:
                a.inference(self.state,agentIndex,action)
            self.gameOver=self.state.isEnd()
            agentIndex=( agentIndex+1 ) % self.rule.numAgent
        
        #inform a learning agent of the game result
        #if "final" in dir(self.agent):
        #   agent.final(self.state)
            
        return self.finish(verbose)
