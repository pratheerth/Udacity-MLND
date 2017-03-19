import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
        
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.q_values = dict() #for storing q values
        self.penalties = [] # list of incurred penalties
        self.penalty = 0
        self.deadlines = [] # list of unsuccessful trials
        self.time_over = 0
    
    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.penalties.append(self.penalty)
        self.deadlines.append(self.time_over)
        

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        # TODO: Update state
        
        current_state = (self.next_waypoint, inputs['light'], inputs['left'], inputs['right'])
        self.state = current_state
        
        q_old, action = self.best_action(self.state)
        
        # Execute action and get reward
        reward = self.env.act(self, action)
        
        if reward < 0:
        	self.penalty += 1
        	
        if deadline < 1:
        	self.time_over += 1
           
                    
        # Sense the environment
            
        new_inputs = self.env.sense(self)
                
        updated_state = (self.next_waypoint, new_inputs['light'], new_inputs['oncoming'], new_inputs['left'], new_inputs['right'])
    
        # Update the Q table
        
        q_new_value = self.calculate_q_value(updated_state, q_old, reward)
        
        self.q_values[(current_state, action)] = q_new_value
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, waypoint = {}".format(deadline, inputs, action, reward, self.next_waypoint)  # [debug]

    #define a function for finding q_max

    def find_q_max(self,updated_state):
    
        # go through the list of q values and for this particular state, action pair, find the q value(s) and store it in variable "q"
        q = [self.get_q(updated_state, action) for action in Environment.valid_actions] #a list to choose in case of q_max.count > 1
        q_max = max(q)
        return q_max, q
        
    
    
    def best_action(self, state):
        
        q_max, list_of_q = self.find_q_max(state)
        
        #In case of multiple q_max, choose randomly
        
        if list_of_q.count(q_max) > 1:
            # making a list of all the max q values for this state,action pair, to randomly choose in case count>1
            max_list_of_q = [i for i in range(len(Environment.valid_actions)) if list_of_q[i] == q_max]
            
            x = random.choice(max_list_of_q)
        
        else:
            
            x = list_of_q.index(q_max)
        
        action = Environment.valid_actions[x]
        
        return q_max, action

    
    # define a function to retrieve to store the q values for each explored state, action pair from self.q_values
    
    def get_q(self, state, action):
        
        return self.q_values.get((state, action), 3.0) # initial q value is 3 to force agent to explore all the states
        
    #calculating q-value
        
    def calculate_q_value(self, updated_state, q_old, reward):
            
        #learning rate
        alpha = 0.5
                
        #discount factor
        gamma = 0.3
                
        learned_value = reward + (gamma * self.find_q_max(updated_state)[0] - q_old)
                                          
        q_new = q_old + alpha * learned_value
                                          
        return q_new
                                          
                                          
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=1.0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    print "The total number of incurred penalties are", a.penalties
    print "The number of unsuccessfull trials", a.deadlines

if __name__ == '__main__':
    run()
                                     

    
