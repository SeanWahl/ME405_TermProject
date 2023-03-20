"""!@file   main.py
@brief      Controls the nerf turret.
@details    Contains all necessary code to be able to use the nerf turret. Please
            see the main page for formal task and state diagrams. Essentially,
            this program sets up all necessary objects and then waits for a 
            user indication to start. Upon a button press or the user entering "s",
            the program will start.
            
            Once started, the program takes a picture of the opposite side of the
            table. With this data, it calculates where the opponent is, and converts
            this into a motor angle. The program then continuously controls the motor
            to go to this angle. Upon 5 seconds (when the opponent is no longer
            able to move) the turret takes another picture and adjusts to this position.
            After 0.5s of adjusting, the gun shoots and then takes another picture.
            This process of taking a picture, calculating an angle, adjusting, and
            shooting continues indefinitely. When a shot count maximum is reached,
            the gun will no longer shoot but will still adjust to point at the
            opponent.
            
            At any point, the user can Ctrl-C or press the blue button again to
            exit the program.
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       March 20, 2023
"""

# Import necessary modules.
import pyb
import math
from nerf import Nerf
from controller import CLController
from motor_driver import MotorDriver
from encoder_reader import encoder
from machine import Pin, I2C
from mlx_cam import MLX_Cam

from time import ticks_ms, ticks_add, ticks_diff

def onButtonPress(IRQ_src):
    """!@brief          Detects interrupt request through blue button press.
        @details        When the button is pressed, this function will set
                        a variable as true, indicating that the button has been
                        pressed and allowing the program to enact on the button
                        press elsewhere.
        @param IRQ_src  Interrupt service request notation. 
    """
    global buttonPressed
    ## Indicates whether or not the blue button has recently been pressed.
    buttonPressed = True

if __name__ == "__main__":
    # The main script of the program. Will set up all necessary objects and then
    # act on states as programmed. Takes care of motor reading/control, camera
    # images, and nerf gun shooting.
    
    ## Serial port object for detecting the user's keyboard inputs, such as "s".
    serport = pyb.USB_VCP()
    
    ## Button interrupt set up for the Nucleo's blue button, attached to pin C13.
    ButtonInt = pyb.ExtInt(pyb.Pin(pyb.Pin.board.PC13), mode=pyb.ExtInt.IRQ_FALLING, pull=pyb.Pin.PULL_NONE, callback=onButtonPress)
    
    # Set up base motor, encoder, and controller objects
    ## Base's motor to move about the yaw axis, turning left and right.
    my_motor_yaw = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    ## Base motor's encoder.
    my_encoder_yaw = encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    # Zero the base motor's encoder.
    my_encoder_yaw.zero()
    ## Base motor's closed loop controller.
    my_controller_yaw = CLController(60, .1, math.pi*16*2.5, 0)
    
    # Set up pitch motor, encoder, and controller objects
    ## Pitch axis's motor to point the gun up and down.
    my_motor_pitch = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    ## Pitch motor's encoder.
    my_encoder_pitch = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    # Zero the pitch motor's encoder.
    my_encoder_pitch.zero()
    ## Pitch motor's closed loop controller.
    my_controller_pitch = CLController(30, .1, 8, 0)
    
    ## Nerf gun object for arming and shooting.
    my_gun = Nerf(Pin.board.PB3, Pin.board.PC4)
    
    # Set up dummy periods for the first run of the tasks.
    ## Period for the controller task in ms.
    cont_per = 10
    ## Initial period for the camera task in ms.
    cam_per  = 5500
    ## Inital period for the nerf gun task in ms.
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
    ## MLX90640's I2C address.
    i2c_address = 0x33
    _scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    print(f"I2C Scan: {_scanhex}")
    
    # Create the camera object and set it up in default mode
    ## The camera object for the MLX90640.
    camera = MLX_Cam(i2c_bus)
    
    # Overall states for this general file. Psuedo states are present though not
    # explicitly called out. Please see the main page.
    ## The state in which user input is waited on to start the control algorithm.
    s0 = 0
    ## The state in which the camera, controller, and nerf gun psuedotasks are run
    #  after user input has been received.
    s1 = 1
    ## The current overall state of the program.
    state = s0
    
    ## Indicates whether or not the blue button has recently been pressed.
    buttonPressed = False
    
    ## How many times the gun has been shot.
    shot_count = 0
    
    print('Press s or the blue button to start.')
    
    while True:
    
        if state == s0:
            # Wait for user input, either a button press or an "s" to start.
            
            # Button press logic.
            if buttonPressed:
                # Reset the button press boolean.
                buttonPressed = False
                
                # Arm the gun.
                my_gun.arm()
                # Zero both encoders.
                my_encoder_yaw.zero()
                my_encoder_pitch.zero()
                ## The time at which the user has started the program, upon
                #  a button press or "s" input.
                t_init = ticks_ms()
                # Go to the pseudotask running state.
                state = s1
                ## The camera's image data.
                image = camera.get_image()
                ## The hottest column of the camera's image.
                column = camera.get_hot_column(image)
                ## The angle at which the yaw motor should turn to in order to
                #  aim at the target.
                motorAngle = .5613 * column + 117.89
                
                # Set the next time for the pseudotasks to run. Note, for the
                # nerf gun this is an arbitrary placeholder time that is just
                # greater than 6 seconds.
                ## The time directly after taking the picture.
                t_rn = ticks_ms()
                ## The time at which the controller task should run again.
                t_next_cont  = ticks_add(t_rn, cont_per)
                ## The time at which the camera task should run again.
                t_next_cam   = ticks_add(t_init, cam_per)
                ## The time at which the nerf gun task should run again.
                t_next_shoot = ticks_add(t_rn, 10_000)
            
            # Check the serial port for an "s" input.
            elif serport.any():
                ## Character data from user's keyboard inputs.
                charIn = serport.read(1).decode()
        
                # Start program if the input is "s".
                if charIn in {'s','S'}:
                    # Arm the gun.
                    my_gun.arm()
                    # Zero both encoders.
                    my_encoder_yaw.zero()
                    my_encoder_pitch.zero()
                    # Set the initial time.
                    t_init = ticks_ms()
                    # Go to the pseudotask running state.
                    state = s1
                    # Take a picture.
                    image = camera.get_image()
                    # Get the hottest column.
                    column = camera.get_hot_column(image)
                    # Calculate where the yaw motor should turn to.
                    motorAngle = .5613 * column + 117.89
                    
                    # Set the next time for the pseudotasks to run. Note, for the
                    # nerf gun this is an arbitrary placeholder time that is just
                    # greater than 6 seconds.
                    t_rn = ticks_ms()
                    t_next_cont  = ticks_add(t_rn, cont_per)
                    t_next_cam   = ticks_add(t_init, cam_per)
                    t_next_shoot = ticks_add(t_rn, 10_000)
                
        if state == s1:
            try:
                
                # If the button is pressed, stop running.
                if buttonPressed:
                    # Reset the button press boolean variable.
                    buttonPressed = False
                    # Disable the motors.
                    my_motor_pitch.set_duty_cycle(0)
                    my_motor_yaw.set_duty_cycle(0)
                    # Disarm the gun.
                    my_gun.disarm()
                    print('Exiting')
                    # Quit the program.
                    break
                
                # Camera pseudotask.
                if ticks_diff(ticks_ms(), t_next_cam) >=0:

                    # Disabling the motors before taking the picture for ~500ms
                    # to avoid issues.
                    my_motor_yaw.set_duty_cycle(0)
                    my_motor_pitch.set_duty_cycle(0)
                    
                    # Get image and calculate yaw motor angle.
                    image = camera.get_image()
                    print('Click')
                    column = camera.get_hot_column(image)
                    motorAngle = .5613 * column + 117.89
                    
                    # Stall next camera shot an arbitrary amount.
                    t_next_cam = ticks_add(ticks_ms(), cam_per)
                    
                    # Tell gun to shoot in .5 seconds to allow for motor adjustment.
                    t_next_shoot = ticks_add(ticks_ms(), 500)
                    
                # Nerf gun psuedotask.
                elif ticks_diff(ticks_ms(), t_next_shoot) >= 0:
                    
                    # Shoot the nerf gun if less than 2 shots have been taken.
                    if shot_count < 2:
                        # Shoot the nerf gun.
                        my_gun.shoot()
                        # Increment the shot counter.
                        shot_count += 1
                        
                    # If the gun has been shot twice, disarm the gun.
                    elif shot_count == 2:
                        # Disarm the nerf gun.
                        my_gun.disarm()
                        # Increment the counter so that this block only runs once.
                        shot_count += 1
                    
                    # Tell camera to take another picture now.
                    t_next_cam = ticks_ms()
                    
                 
                # Controller psuedotask.
                elif ticks_diff(ticks_ms(), t_next_cont) >= 0:
                    # Tell the task to run again in 10ms if possible.
                    t_next_cont = ticks_add(ticks_ms(), cont_per)
                    
                    # Set yaw motor controls.
                    # Update the yaw motor.
                    my_encoder_yaw.read_encoder()
                    # Update the controller's positional set point.
                    my_controller_yaw.set_Pos(motorAngle)
                    ## The duty cycle applied to the yaw motor, calculated through
                    #  a closed loop control law.
                    actuation_yaw = my_controller_yaw.run(my_encoder_yaw.read_Posrad(), my_encoder_yaw.read_Velrad())
                    # Apply the actuation value to the yaw motor.
                    my_motor_yaw.set_duty_cycle(actuation_yaw)
                    
                    # Set pitch motor controls. Note, the pitch motor is kept at
                    # constant angle.
                    # Update the pitch motor.
                    my_encoder_pitch.read_encoder()
                    ## The duty cycle applied to the pitch motor, calculated through
                    #  a closed loop control law.
                    actuation_pitch = my_controller_pitch.run(my_encoder_pitch.read_Posrad(), my_encoder_pitch.read_Velrad())
                    # Apply the actuation value to the pitch motor.
                    my_motor_pitch.set_duty_cycle(actuation_pitch)
                
            except KeyboardInterrupt:
                # If Ctrl+C is entered, disable the motors.
                my_motor_pitch.set_duty_cycle(0)
                my_motor_yaw.set_duty_cycle(0)
                # Disarm the gun.
                my_gun.disarm()
                print('Exiting')
                # Exit the program.
                break

