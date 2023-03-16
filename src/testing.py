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

def onButtonPress(IRQ_src):
    '''!@brief          Detects interrupt request through button press.
        @details        When the button is pressed, this function will set
                        a variable as true, indicating that the button has been
                        pressed and allowing the script to enact on the button
                        press elsewhere.
        @param IRQ_src  Interrupt service request notation. 
    '''
    global buttonPressed
    buttonPressed = True

if __name__ == "__main__":
    
    # Set up serial port
    serport = pyb.USB_VCP()
    
    # Set up button interrupt
    ButtonInt = pyb.ExtInt(pyb.Pin(pyb.Pin.board.PC13), mode=pyb.ExtInt.IRQ_FALLING, pull=pyb.Pin.PULL_NONE, callback=onButtonPress)
    
    # Set up base motor, encoder, and controller objects
    my_motor_yaw = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    my_encoder_yaw = encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    my_encoder_yaw.zero()
    my_controller_yaw = CLController(60, .1, math.pi*16*2.5, 0)
    
    # Set up pitch motor, encoder, and controller objects
    my_motor_pitch = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    my_encoder_pitch = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    my_encoder_pitch.zero()
    my_controller_pitch = CLController(30, .1, 8, 0)
    
    # Set up nerf object
    my_gun = Nerf(Pin.board.PB3, Pin.board.PC4)
    
    cont_per = 10
    cam_per  = 5500
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

    s0 = 0
    s1 = 1
    state = s0
    
    buttonPressed = False
    print('Press s to start')
    
    shot_count = 0
    
    while True:
    
        if state == s0:
            if buttonPressed:
                buttonPressed = False

                my_gun.arm()
                my_encoder_yaw.zero()
                my_encoder_pitch.zero()
                t_init = ticks_ms()
                state = s1
                image = camera.get_image()
                column = camera.get_hot_column(image)
                motorAngle = .5613 * column + 117.89
                
                t_rn = ticks_ms()
                t_next_cont  = ticks_add(t_rn, cont_per)
                t_next_cam   = ticks_add(t_init, cam_per)
                t_next_shoot = ticks_add(t_rn, 10_000)
                
            elif serport.any():
                ## @brief Character data from user's keyboard inputs.
                #
                charIn = serport.read(1).decode()
        
                #Set state according to user input
                if charIn in {'s','S'}:
                    my_gun.arm()
                    my_encoder_yaw.zero()
                    my_encoder_pitch.zero()
                    t_init = ticks_ms()
                    state = s1
                    image = camera.get_image()
                    column = camera.get_hot_column(image)
                    motorAngle = .5613 * column + 117.89
                    
                    t_rn = ticks_ms()
                    t_next_cont  = ticks_add(t_rn, cont_per)
                    t_next_cam   = ticks_add(t_init, cam_per)
                    t_next_shoot = ticks_add(t_rn, 10_000)
                    
                elif charIn in {'p', 'P'}:
                    image = camera.get_image()
                    column = camera.get_hot_column(image)
                    angle  = (172.76 + (column - 8) * 0.8512)*math.pi/180
                    # 0.812 [deg/pixels]
                    print(column)
                
                elif charIn in {'r', 'R'}:
                    print(my_encoder.read_Posrad())
                    
                my_encoder_yaw.read_encoder()
                my_encoder_pitch.read_encoder()
                
        if state == s1:
            try:
                if buttonPressed:
                    buttonPressed = False
                    my_motor_pitch.set_duty_cycle(0)
                    my_motor_yaw.set_duty_cycle(0)
                    my_gun.disarm()
                    print('Exiting')
                    break
                
                # Camera code   
                if ticks_diff(ticks_ms(), t_next_cam) >=0:

                    # Disabling motors
                    my_motor_yaw.set_duty_cycle(0)
                    my_motor_pitch.set_duty_cycle(0)
                    
                    # Get image and calculate yaw motor angle
                    image = camera.get_image()
                    print('Click')
                    column = camera.get_hot_column(image)
                    motorAngle = .5613 * column + 117.89
                    
                    # Stall next camera shot
                    t_next_cam = ticks_add(ticks_ms(), cam_per)
                    
                    # Tell gun to shoot in .5 seconds
                    t_next_shoot = ticks_add(ticks_ms(), 500)
                    
                # Gun code
                elif ticks_diff(ticks_ms(), t_next_shoot) >= 0:
                    
                    if shot_count < 2:
                        # Shoot gun
                        my_gun.shoot()
                        shot_count += 1
                        
                    elif shot_count == 2:
                        my_gun.disarm()
                        shot_count += 1
                    
                    # Tell camera to take another picture
                    t_next_cam = ticks_ms()
                    
                 
                # Controller code
                elif ticks_diff(ticks_ms(), t_next_cont) >= 0:
                    t_next_cont = ticks_add(ticks_ms(), cont_per)
                    
                    # Set yaw motor controls
                    my_encoder_yaw.read_encoder()
                    my_controller_yaw.set_Pos(motorAngle)
                    actuation = my_controller_yaw.run(my_encoder_yaw.read_Posrad(), my_encoder_yaw.read_Velrad())
                    my_motor_yaw.set_duty_cycle(actuation)
                    
                    # Set pitch motor controls
                    my_encoder_pitch.read_encoder()
                    actuation = my_controller_pitch.run(my_encoder_pitch.read_Posrad(), my_encoder_pitch.read_Velrad())
                    my_motor_pitch.set_duty_cycle(actuation)
                
            except KeyboardInterrupt:
                my_motor_pitch.set_duty_cycle(0)
                my_motor_yaw.set_duty_cycle(0)
                my_gun.disarm()
                print('Exiting')
                break

