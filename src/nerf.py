from pyb import Pin
import pyb

class Nerf:
    
    def __init__(self, armPin, shootPin):
        self.armPin = Pin(armPin, Pin.OUT)
        self.armPin.low()
        self.shootPin = Pin(shootPin, Pin.OUT)
        self.shootPin.low()
        self.armed = False
        
    def arm(self):
        self.armPin.high()
        self.armed = True
        print('Armed Captain')
        
    def disarm(self):
        self.armPin.low()
        self.armed = False
        print('Standing down')
        
    def shoot(self):
        if self.armed == True:
            self.shootPin.high()
            pyb.delay(50)
            self.shootPin.low()
        else:
            print('Not ready!')
            
if __name__ == "__main__":
    import pyb
    
    myGun = Nerf(Pin.board.PB3, Pin.board.PC4)
    myGun.arm()
    pyb.delay(1000)
    myGun.disarm()
    myGun.shoot()
    pyb.delay(1000)
    myGun.arm()
    pyb.delay(1000)
    myGun.shoot()
    pyb.delay(1000)
    myGun.disarm()
    