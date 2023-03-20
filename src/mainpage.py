'''!@file                mainpage.py
    @brief               Welcome to mecha15's Term Project page!
    @details             In this portfolio we will be documenting all of the working
                         code necessary for our heat-seeking nerf turret for future
                         reference and display. Feel free to look around and contact
                         us if necessary.
                         
    @mainpage
    
    @section desc       Overview
                        In this project, we were tasked with building a 2-DOF
                        nerf sentry turret. This entailed creating a structure
                        that was capable of holding a projectile launcher (nerf
                        gun) and moving it about the conventional yaw and pitch
                        axes. 
                        
                        Over the course of several weeks, we constructed the
                        following device.
                        
                        @image html Turret.jpeg width=400 height=500
                        
                        This turret is capable of all project requirements and
                        worked well in practice. Our one fatal error was human
                        negligence (we forgot to load the gun in the final round
                        of the competition). 
                        
                        All code that will be referenced in this portfolio
                        is accessible through https://github.com/SeanWahl/ME405_TermProject .
                        However, you may find it more useful to read through the 
                        documentation found here first, as it will be formatted
                        better than just a python file.

    @section files      Necessary Files
                        In order to be able to use the nerf turret, you will need 
                        6 files along with a few support files. These files are 
                        listed below with a short description.
                        
                        encoder_reader.py - Sets up an encoder to interface with 
                                            its associated motor. Allows for
                                            angular position and velocity readings
                                            if updated frequently enough.
                        
                        motor_driver.py - Sets up a motor to have a duty cycle
                                          applied. Allows for the motor to be
                                          enabled or disabled as well.
                        
                        controller.py - Sets up a closed loop controller. Allows
                                        for proportional and derivated control. An
                                        example use case of this would be using
                                        an encoder's readings to calculate a duty
                                        cycle for a motor in order to control its
                                        position.
                        
                        nerf.py - Sets up a nerf gun object. Allows for arming
                                  and disarming of the gun's flywheels, and also
                                  allows for shooting a dart but only if the gun
                                  is armed.
                        
                        mlx_cam.py - Sets up a camera object. The MLX 90640 is
                                     capable of taking thermal pictures with dimensions
                                     of 32x24 pixels. The actual set up of this
                                     camera is outside the scope of the class, 
                                     and the files presented in mlx90640 had been
                                     provided to us. We added one function to this
                                     file in order to calculate which column of the
                                     camera had the hottest readings.
                        
                        main.py - Utilizes all files previously listed to set up
                                  our nerf turret. Periodically runs one of three
                                  tasks in our own task-based structure that allows
                                  for running tasks with variable periods. Please
                                  see the section below for more details on the 
                                  structure of the file.
                
                        
                        

    @section states     Task and State Diagrams
                        In lieu of using the instructor provided task files, we
                        created our own task based structure in a python file.
                        This is technically only one task, though it allows for
                        variable periods in our tasks and eliminates problems we
                        were running into with the instructor's files in which the
                        tasks caused massive delays if they weren't being run on time.
                        It was guaranteed that they would not run on time because
                        the camera uses blocking code to take the picture. The
                        proper overall state transition diagram for our system is as
                        follows:
                            
                        @image html STD.jpg width=900
                        
                        Though main.py technically only has one task, the states
                        present in it represent tasks in themselves. We can make
                        a psuedo-task diagram to understand their relationships.
                        
                        @image html psuedoTasks.jpg width=550
                        
                        By using this structure, we are essentially setting flags
                        for when the camera and nerf tasks should run. We think
                        that setting periods in the traditional task structure 
                        could work, though we are unsure why cotask was giving
                        us issues with running tasks on time. We believe it is
                        becuase the camera would take around 500ms to take a picture,
                        stalling the code during this time and then rushing to make
                        up other tasks afterwards.
                        
                        Our approach worked well for the assignment at hand, especially
                        with the dynamic series of events that needed to take place
                        for the duel. After an initial picture is taken, we turn
                        around and wait the 5 seconds until the target stops moving.
                        Then, we take another picture, aim for 500ms, and fire. This cycle
                        goes on until a maximum number of shots is reached, at which
                        the gun will track the target without shooting. At any point
                        the program can be exited with a Ctrl-C or button press
                        on the Nucleo. 
                        
    @author              Nathan Dodd
    @author              Lewis Kanagy
    @author              Sean Wahl

    @date                March 20, 2023
'''