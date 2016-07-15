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
        self.Qtable = {}
        self.alpha = 0.8
        self.gamma = 0.6

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'])
        old_state = self.state
        
        # TODO: Select action according to your policy
        if (old_state, None) not in self.Qtable.keys():
            self.Qtable[(old_state, None)] = 0
        if (old_state, 'left') not in self.Qtable.keys():
            self.Qtable[(old_state, 'left')] = 0
        if (old_state, 'forward') not in self.Qtable.keys():
            self.Qtable[(old_state, 'forward')] = 0
        if (old_state, 'right') not in self.Qtable.keys():
            self.Qtable[(old_state, 'right')] = 0
        
        max_action = max(self.Qtable[(old_state, None)], self.Qtable[(old_state, 'left')],self.Qtable[(old_state, 'forward')],self.Qtable[(old_state, 'right')])
        action = random.choice([ i for i in ['left', 'forward', 'right', None] if self.Qtable[(old_state, i)] == max_action])

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        #self.next_waypoint = self.planner.next_waypoint()
        inputs = self.env.sense(self)
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'])
        new_state = self.state

        if (new_state, None) not in self.Qtable.keys():
            self.Qtable[(new_state, None)] = 0
        if (new_state, 'left') not in self.Qtable.keys():
            self.Qtable[(new_state, 'left')] = 0
        if (new_state, 'forward') not in self.Qtable.keys():
            self.Qtable[(new_state, 'forward')] = 0
        if (new_state, 'right') not in self.Qtable.keys():
            self.Qtable[(new_state, 'right')] = 0

        self.Qtable[(old_state, action)] = (1 - self.alpha) * self.Qtable[(old_state, action)] + self.alpha *(reward + self.gamma * max(self.Qtable[(new_state, i)] for i in [None, 'left', 'forward', 'right']))




        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False
    sim.run(n_trials=100)  # run for a specified number of trials

    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
