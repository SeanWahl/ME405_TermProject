"""!@file encoder_reader.py
@brief      Documents the encoder class for ME 405.
@details    Contains the "encoder" class that can be used to set up encoder objects
            that will be used in future labs. Encoders are able to sense positional
            changes, allowing for angle control or rotational speed calculations.
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       January 31, 2023
"""

# Import necessary modules.
import time, pyb, math

class encoder:
    """!@brief      Implements an encoder class to be used in lab.
       @details     An encoder class compatible with the encoders in the ME 405 lab
                    kits. Allows for functions such as reading and zeroing.
    """
    
    def __init__(self, pin1, pin2, timer):
        """!@brief          Initializes an encoder object.
            @details        Using pin objects as inputs, is able to create an encoder
                            capable of sensing positional changes through the use of
                            the timer's counting ability.
            @param pin1     Pin object connected to encoder channel A. 
            @param pin2     Pin object connected to encoder channel B.
            @param timer    Timer channel (has to be compatible with pins 1 and 2)
        """
        ## Pin object representing the connection to channel A of the encoder.
        self.pin1 = pyb.Pin(pin1, pyb.Pin.OUT_PP)
        ## Pin object representing the connection to channel B of the encoder.
        self.pin2 = pyb.Pin(pin2, pyb.Pin.OUT_PP)
        ## Timer object used for adding the encoder's positional changes.
        self.timer = pyb.Timer (timer, period = 0xFFFF, prescaler = 0)
        ## Channel associated with channel A of the encoder, will count in one direction.
        self.ch1 = self.timer.channel(1, pyb.Timer.ENC_AB, pin=self.pin1)
        ## Channel associated with channel B of the encoder, will count in the opposite direction.
        self.ch2 = self.timer.channel(2, pyb.Timer.ENC_AB, pin=self.pin2)
        ## Overall position of the encoder in ticks.
        self.count = 0
        ## The previous timer count value.
        self.prev = 0
        
        # Time and position lists for velocity calculation.
        self._timelist = [0]*5
        self._poslist = [0]*5
        
    def read_encoder(self):
        """!@brief          Retrieves the overall position of the encoder.
            @return         The total position of the encoder in ticks.
        """
        ## The current timer count value.
        self.current = self.timer.counter()
        ## The change in timer count value from the last update.
        self.delta = self.current-self.prev
        # Check for overflow/underflow
        if abs(self.delta) > (0xFFFF+1)/2:
            if self.delta > 0:
                self.count -= self.delta - 0xFFFF
            else:
                self.count -= self.delta + 0xFFFF
        else:
            self.count -= self.delta
        
        # Append the position and time lists as necessary.
        self._poslist.pop(0)
        self._poslist.append(self.count)
        self._timelist.pop(0)
        self._timelist.append(time.ticks_us())
        
        self.prev = self.current
        return self.count
        
    def read_Posrad(self):
        """!@brief          Retrieves the overall position of the encoder in radians.
            @return         The total position of the encoder in radians.
        """
        return self.read_encoder()*2*math.pi/(256*4)
    
    def read_omega(self):
        """!@brief          Retrieves the rotational velocity of the encoder.
            @return         The rotational velocity of the encoder in ticks/second.
        """
        omega = (self._poslist[0]-self._poslist[4])/(time.ticks_diff(self._timelist[0], self._timelist[4])/1000000)
        return omega
    
    def read_Velrad(self):
        """!@brief		Retrieves the rotational velocity of the encoder in radians/s.
            @return     The rotational velocity of the encoder in r/s.
        """
        return self.read_omega()*2*math.pi/(256*4)
    
    def zero(self):
        """!@brief          Sets the encoder's overall position value back to zero.
        """
        self.count = 0
        self.prev = self.timer.counter()
        
if __name__ == "__main__":
    #Set up an encoder, have it read 9 times and zero on the tenth.
    #my_encoder = encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    my_encoder = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    my_encoder.zero()
    while True:
        for n in range(100):
            my_encoder.read_encoder()
        if n == 99:
            print(f'pos:{my_encoder.read_Posrad()}, vel:{my_encoder.read_Velrad()}')
        time.sleep(0.010)