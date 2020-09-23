from transitions import Machine
import time

class RobotState(object):

    # Define states. 
    states = ['INIT', 'CALLED', 'ARRIVED', 'LOADED']

    def __init__(self):

        # Initialize the state machine
        self.machine = Machine(model=self, states=RobotState.states, initial='INIT')

        # Transitions. 
        self.machine.add_transition(trigger='call_robot', source='INIT', dest='CALLED', after='called_session')

        self.machine.add_transition(trigger='cancel_robot', source='CALLED', dest='INIT', after='canceled_session')
        
        self.machine.add_transition(trigger='cancel_load', source='ARRIVED', dest='INIT', after='canceled_load_session')
       
        self.machine.add_transition(trigger='robot_arrived', source='CALLED', dest='ARRIVED', after='arrived_session')
        
        self.machine.add_transition(trigger='robot_loaded', source='ARRIVED', dest='LOADED', after='loaded_session')
        
        self.machine.add_transition(trigger='user_reset', source='LOADED', dest='INIT', after='reset_session')

    def called_session(self):
        
        print("Now in state: " +  self.state);
        
    def canceled_session(self):
        
        print("Now in state: " +  self.state);
    
    def canceled_load_session(self):
        
        print("Now in state: " +  self.state);
       
    def arrived_session(self):
        
        print("Now in state: " +  self.state);
        
    def loaded_session(self):
        
        print("Now in state: " +  self.state);
        
    def reset_session(self):
        
        print("Now in state: " +  self.state);
        
        
        
        
