from transitions import Machine
import time

class RobotState(object):

    # Define some states. 
    states = ['init', 'called']

    def __init__(self):

        # Initialize the state machine
        self.machine = Machine(model=self, states=RobotState.states, initial='init')

        # Add some transitions. 
        self.machine.add_transition(trigger='call_robot', source='init', dest='called', after='called_session')

        self.machine.add_transition(trigger='cancel_robot', source='called', dest='init', after='canceled_session')


    def called_session(self):
        
        print("Now in state: " +  self.state);
        
    
    def canceled_session(self):
        
        print("Now in state: " +  self.state);
       

        
        
        
        