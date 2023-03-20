"""!@file   nerf.py
@brief      Documents the nerf gun class for ME 405.
@details    Contains the "nerf" class that can be used to set up a nerf gun object
            that will be used for our nerf sentry turret term project. The nerf gun
            is able to be armed/disarmed and can shoot when armed.
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       March 20, 2023
"""

# Import necessary modules.
from pyb import Pin
import pyb

class Nerf:
    """!@brief      Implements a nerf gun class to use for the term project.
       @details     An nerf gun class compatible with the Snowcinda toy machine
                    gun. Assumes that the trigger and safety mechanisms have been
                    altered to be shorted by two GPIO pins and external hardware.
                    Once set up properly, activating the two pins will either arm
                    or shoot the gun.
    """
    def __init__(self, armPin, shootPin):
        """!@brief          Initializes a nerf gun object.
            @details        Using pin objects as inputs, is able to create a nerf
                            gun object. External hardware should be connected such
                            that setting the armPin to high will short the flywheel's
                            wires, and setting the shootPin to high will short the
                            piston arm's wires.
            @param armPin   The pin set up to arm the gun's flywheels when high.
            @param shootPin The pin set up to shoot a dart when the flywheels are
                            armed.
        """
        ## The pin object that will arm the gun's flywheels when set high.
        self.armPin = Pin(armPin, Pin.OUT)
        # Make sure the gun is disarmed to start.
        self.armPin.low()
        ## The pin object that will be able to shoot a dart if the gun is armed.
        self.shootPin = Pin(shootPin, Pin.OUT)
        # Make sure the gun is not shooting.
        self.shootPin.low()
        ## A boolean object indicating if the gun is armed or not.
        self.armed = False
        
    def arm(self):
        """!@brief      Arms the nerf gun by setting the armPin to high.
        """
        # Arm the gun.
        self.armPin.high()
        # Set the armed boolean to True.
        self.armed = True
        print('Armed Captain')
        
    def disarm(self):
        """!@brief      Disarms the nerf gun by setting the armPin to low.
        """
        # Disarm the gun.
        self.armPin.low()
        # Set the armed boolean to False.
        self.armed = False
        print('Standing down')
        
    def shoot(self):
        """!@brief      Shoots the gun, but only if the gun is armed.
        """
        # If the gun is armed, shoot.
        if self.armed == True:
            # Toggle the shoot pin for 50 ms to make sure it shoots.
            self.shootPin.high()
            pyb.delay(50)
            self.shootPin.low()
        else:
            print('Not ready!')
            
if __name__ == "__main__":
    # Set up a nerf gun object for testing.
    myGun = Nerf(Pin.board.PB3, Pin.board.PC4)