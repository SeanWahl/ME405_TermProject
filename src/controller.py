"""!@file controller.py
@brief      Documents the controller class for ME 405.
@details    Contains the "controller" class that can be used to set up controller objects
            that will be used in labs to do closed loop control on various devices,
            like positional control of a motor. This class will be general enough to
            do this for any device by only using only gains, setpoints, and measurements
            to calculate actuation signals.  
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       February 7, 2023
"""

# Import necessary modules for the testing section.
from motor_driver import MotorDriver
from encoder_reader import encoder
import utime, pyb, math

class CLController:
    """!@brief      Implements a controller class to be used in lab.
       @details     A controller class versatile enough to be used with several
                    devices in the ME 405 lab kits, such as motors and encoders. 
                    Allows for functions such as calculating actuation signals
                    and setting gains and setpoints for the controller's calculations.
    """
    
    def __init__(self, Kp, Kd, PosSet, VelSet):
        """!@brief             Initializes a controller object.
            @details           Creates a controller object with a specified initial
                               gain and setpoint, though these can be changed 
                               through various methods.
            @param   Kp        The controller's proportional gain.
            @param   Kd        The controller's derivative gain. 
            @param   PosSet    The controller's positional setpoint.
            @param   VelSet    The controller's velocity setpoint.
        """   
        ## The controller's proportional gain, to be used in closed loop control.
        self.Kp = Kp
        ## The controller's derivative gain, to be used in closed loop control.
        self.Kd = Kd
        ## The controller's positional setpoint, which it tries to reach in closed loop control.
        self.PosSet = PosSet
        ## The controller's velocity setpoint, which it tries to reach in closed loop control.
        self.VelSet = VelSet
    
    def run(self, ActPos, ActVel):
        """!@brief		    Calculates the actuation signal based on the error of
                            the measured reading from the setpoint.
            @param  ActPos  The actual, measured position reading from a device
            @param  ActOme  The actual, measured velocity reading from a device
            @return         The actuation signal necessary to drive the measured
                            signal towards the setpoint.
        """
        ## The actuation signal necessary to drive the measured signal towards the
        #  setpoints.
        Actuation = self.Kp * (self.PosSet - ActPos) + self.Kd * (self.VelSet - ActVel)
        return Actuation
    
    def set_Kp(self, Kp):
        """!@brief		Sets the controller's proportional gain value.
            @param  Kp  The controller's proportional gain.
        """
        self.Kp = Kp
        
    def set_Kd(self, Kd):
        """!@brief		Sets the controller's derivative gain value.
            @param  Kd  The controller's derivative gain.
        """
    
    def set_Pos(self, PosSet):
        """!@brief		      Sets the controller's positional setpoint value.
            @param  Setpoint  The controller's positional setpoint.
        """
        self.PosSet = PosSet
        
    def set_Vel(self, VelSet):
        """!@brief		      Sets the controller's positional setpoint value.
            @param  VelSet    The controller's velocity setpoint.
        """
        self.PosSet = VelSet        
        
if __name__ == "__main__":
    # Set up base motor, encoder, and controller objects
    #my_motor = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    #my_encoder = encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    #my_controller = CLController(20, 1.5, math.pi*16*2.5, 0)
    
    # Set up pitch motor, encoder, and controller etc.
    my_motor = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    my_encoder = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    my_controller = CLController(10, .2, math.pi*16, 0)
    
    # Zero the encoder
    my_encoder.zero()
    print(my_encoder.read_Posrad())
    
    # Use the controller to set the motor's duty cycle to try and reach the setpoint
    # over 5 seconds.
    for idx in range(500):
        my_encoder.read_encoder()
        my_motor.set_duty_cycle(my_controller.run(my_encoder.read_Posrad(),my_encoder.read_Velrad()))
        utime.sleep_ms(10)
    print('done')
    
    # Check the encoder's final position reading and turn off the motor.
    print(my_encoder.read_Posrad())
    my_motor.set_duty_cycle(0)