import gc
import pyb
import math
import cotask
import task_share
from nerf import Nerf
from controller import CLController
from motor_driver import MotorDriver
from encoder_reader import encoder
from machine import Pin, I2C
from mlx_cam import MLX_Cam

from time import ticks_ms, ticks_add, ticks_diff

if __name__ == "__main__":
    
    # Set up serial port
    serport = pyb.USB_VCP()
    
    # Set up base motor, encoder, and controller objects
    my_motor = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    my_encoder = encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    my_encoder.zero()
    my_controller = CLController(20, .5, math.pi*16*2.5, 0)
    
    # Set up nerf object
    my_gun = Nerf(Pin.board.PB3, Pin.board.PC4)
    
    t_init = ticks_ms()
    
    cont_per = 10
    cam_per  = 2000
    shoot_per = 4500
    
    try:
        from pyb import info

    # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
    except ImportError:
        # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
        i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))

    # OK, we do have an STM32, so just use the default pin assignments for I2C1
    else:
        i2c_bus = I2C(1)

    # Select MLX90640 camera I2C address, normally 0x33, and check the bus
    i2c_address = 0x33
    scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    print(f"I2C Scan: {scanhex}")
    
    # Create the camera object and set it up in default mode
    camera = MLX_Cam(i2c_bus)
    image = camera.get_image()
    column = camera.get_hot_column(image)
    angle  = (172.76 + (column - 8) * 0.8512)*math.pi/180
    
    s0 = 0
    s1 = 1
    state = s0
    
    print('Press s to start')
    
    while True:
        if state == s0:
            if serport.any():
                ## @brief Character data from user's keyboard inputs.
                #
                charIn = serport.read(1).decode()
        
                #Set state according to user input
                if charIn in {'s','S'}:
                    my_gun.arm()
                    my_encoder.zero()
                    state = s1
                    image = camera.get_image()
                    column = camera.get_hot_column(image)
                    angle  = (172.76 + (column - 8) * 0.8512)*math.pi/180
                    t_rn = ticks_ms()
                    t_next_cont  = ticks_add(t_rn, cont_per)
                    t_next_cam   = ticks_add(t_rn, cam_per)
                    t_next_shoot = ticks_add(t_rn, shoot_per)
            
        if state == s1:
            try:
                
                # Gun code
                if ticks_diff(ticks_ms(), t_next_shoot) >= 0:
                    t_next_shoot = ticks_add(ticks_ms(), shoot_per)
                    
                    my_gun.shoot()
                    
                # Camera code   
                if ticks_diff(ticks_ms(), t_next_cam) >=0:
                    t_next_cam = ticks_add(ticks_ms(), cam_per)
                    
                    my_motor.set_duty_cycle(0)
                    image = camera.get_image()
                    column = camera.get_hot_column(image)
                    angle  = (172.76 + (column - 8) * 0.8512)*math.pi/180
                    
                # Controller code
                if ticks_diff(ticks_ms(), t_next_cont) >= 0:
                    t_next_cont = ticks_add(ticks_ms(), cont_per)
                    
                    my_encoder.read_encoder()
                    my_controller.set_Pos(angle*16*2.5)
                    actuation = my_controller.run(my_encoder.read_Posrad(), my_encoder.read_Velrad())
                    my_motor.set_duty_cycle(actuation)
                
            except KeyboardInterrupt:
                my_motor.set_duty_cycle(0)
                my_gun.disarm()
                print('Exiting')
                break

