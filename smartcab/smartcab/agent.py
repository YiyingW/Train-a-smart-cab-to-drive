import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from collections import namedtuple
import pickle

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {}

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def sign(self, a, b):
    	# a, b are tuples. (a[0], a[1]), (b[0], b[1])
    	# return a tuple, representing the sign of a - b: (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), ...
    	x, y = None, None
    	if a[0] > b[0]:
    		x = 1
    	elif a[0] == b[0]:
    		x = 0
    	else:
    		x = -1
    	if a[1] > b[1]:
    		y = 1
    	elif a[1] == b[1]:
    		y = 0
    	else:
    		y = -1
    	return (x, y)

    def update(self, t):
        # Gather inputs
        inputs = self.env.sense(self)  # self is the Agent object
        deadline = self.env.get_deadline(self)
        agent_states = self.env.agent_states[self]

        # TODO: Update state
        States = namedtuple("States", "Location Heading Destination Deadline Light Oncoming Left Right")
        self.state = States(agent_states["location"],agent_states["heading"],agent_states["destination"],agent_states["deadline"] ,inputs.light,inputs.oncoming, inputs.left, inputs.right)
        current_state = self.state


        current_relative_loc = self.sign(self.state.Destination, self.state.Location)
        # TODO: Select action according to your policy
        if (current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, None) not in self.Q.keys():
            self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, None)] = 0
        if (current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right,'forward') not in self.Q.keys():
            self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right,'forward')] = 0
        if (current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, 'left') not in self.Q.keys():
            self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, 'left')] = 0
        if (current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, 'right') not in self.Q.keys():
            self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right,'right')] = 0


        max_action = max(self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, None)],self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, 'forward')],self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, 'left')],self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, 'right')])
        action = random.choice([i for i in ['left', 'forward', 'right', None] if self.Q[(current_relative_loc, self.state.Heading, self.state.Light, self.state.Oncoming, self.state.Left, self.state.Right, i)] == max_action])
        self.next_waypoint = action  # from route planner, also displayed by simulator
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        new_inputs = self.env.sense(self)
        new_state = States(agent_states["location"],agent_states["heading"],agent_states["destination"],agent_states["deadline"] ,new_inputs.light, new_inputs.oncoming, new_inputs.left, new_inputs.right)
        new_relative_loc = self.sign(new_state.Destination, new_state.Location)
        if (new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, None) not in self.Q.keys():
            self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, None)] = 0
        if (new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'forward') not in self.Q.keys():
            self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'forward')] = 0
        if (new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'left') not in self.Q.keys():
            self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'left')] = 0
        if (new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'right') not in self.Q.keys():
            self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'right')] = 0
        
        max_of_next = max([self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, None)],self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'forward')],self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'left')],self.Q[(new_relative_loc, new_state.Heading, new_state.Light, new_state.Oncoming, new_state.Left, new_state.Right, 'right')]])
        # update the Q
        self.Q[(current_relative_loc, current_state.Heading, current_state.Light, current_state.Oncoming, current_state.Left, current_state.Right, action)] = reward + 0.8*max_of_next
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        print "*************************", len(self.Q), "*************************"





def main():
    """Run the agent for a finite number of trials."""
    # Set up environment and agent

    file = open('Q_rewardV3.pickle', 'r')
    Q = pickle.load(file)
    file.close()

    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    a.Q = Q
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track

    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=1, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False



    sim.run(n_trials=1000)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
   

    f = open('Q_rewardV3.pickle', 'w')
    pickle.dump(a.Q, f)
    f.close()

    
    





if __name__ == '__main__':
    main()

