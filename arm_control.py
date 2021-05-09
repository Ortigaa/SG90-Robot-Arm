#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:28:46 2020

@author: rodri

Module Documantation:
    
    
"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    import os
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import constants
    from scipy import interpolate
    import scipy.integrate as integrate
    import scipy as scy
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox
    import serial
    import pickle as pk
    
except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))
    
# =============================================================================
# Your code starts here
# =============================================================================

# =============================================================================
# Set up GUI
# =============================================================================
window = tk.Tk()

window.geometry('750x550')
window.title("Arm Control")
window.resizable(False, False)


# =============================================================================
# Define functions of system
# =============================================================================
def find_ports(directory):
    names = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.startswith('ttyUSB'):
                names.append(directory+name)
    return names

def find_saved_positions(directory):
    files = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith('.pos'):
                files.append(directory+name)
    return files


# =============================================================================
# Create some global variables to use through the program
# =============================================================================
baudrate = 9600
port_list = find_ports('/dev/')
port_list.insert(0, "-- select --")
status_colors = {"ON":"green", "OFF":"red"}
connection_status = "OFF"
open_status = "OFF"
close_status = "ON"
servos = {"base":0, "shoulder":1, "elbow":2, "wrist":3, "clamp":4}
saved_programs = ["--select--"]
# new_programs = find_saved_positions('/home/rodri/Documentos/Python/robot_arm/')



# =============================================================================
# Define different functions for the menu buttons
# =============================================================================

# Dummy function for the buttons
def donothing():
    filewin = tk.Toplevel(window)
    button = tk.Button(filewin, text="Do nothing button")
    button.pack()


def connectToArduino():
    # =============================================================================
    # Receive and send instructions to Arduino
    # =============================================================================
    try:
        try:
            global ArduinoSerial
            ArduinoSerial = serial.Serial(selected_port, baudrate)
            if ArduinoSerial.readline():
                global connection_status
                connection_status = "ON"
                status_led.create_oval(coord, fill=status_colors[connection_status])
            else:
                messagebox.showwarning("Warning", "Connection can not be stablished")
        except serial.serialutil.SerialException:
            pass
    except NameError:
        messagebox.showwarning("Warning","No port has been selected")
  
def closeConnection():
    ArduinoSerial.close()
    global connection_status
    connection_status = "OFF"
    status_led.create_oval(coord, fill=status_colors[connection_status])
    
def singleMove_base():
    if connection_status == "OFF":
       messagebox.showerror("Error", "No connection found")
    else:
        text_to_send = "<"+str(0)+","+str(base_slider.get())+">"
        print(text_to_send)
        ArduinoSerial.write(text_to_send.encode("utf-8"))
    
def singleMove_shoulder():
    if connection_status == "OFF":
       messagebox.showerror("Error", "No connection found")
    else:
        text_to_send = "<"+str(1)+","+str(shoulder_slider.get())+">"
        print(text_to_send)
        ArduinoSerial.write(text_to_send.encode("utf-8"))

def singleMove_elbow():
    if connection_status == "OFF":
       messagebox.showerror("Error", "No connection found")
    else:
        text_to_send = "<"+str(2)+","+str(elbow_slider.get())+">"
        print(text_to_send)
        ArduinoSerial.write(text_to_send.encode("utf-8"))
  
def singleMove_wrist():
    if connection_status == "OFF":
       messagebox.showerror("Error", "No connection found")
    else:
        text_to_send = "<"+str(3)+","+str(wrist_slider.get())+">"
        print(text_to_send)
        ArduinoSerial.write(text_to_send.encode("utf-8"))
        
def openClamp():
    if connection_status == "OFF":
       messagebox.showerror("Error", "No connection found")
    else:
        text_to_send = "<"+str(4)+","+str(40)+">"
        print(text_to_send)
        ArduinoSerial.write(text_to_send.encode("utf-8"))

def closeClamp():
    if connection_status == "OFF":
       messagebox.showerror("Error", "No connection found")
    else:
        text_to_send = "<"+str(4)+","+str(0)+">"
        print(text_to_send)
        ArduinoSerial.write(text_to_send.encode("utf-8"))
  

def ComboboxPort(event):
    global selected_port
    selected_port = port_select.get()

def savePosition():
    positions = [base_slider.get(), shoulder_slider.get(), elbow_slider.get(), wrist_slider.get(), close_status]
    file_name = save_position_name.get()
    print(positions)
    with open(file_name+".pos", "wb") as out_file:
            pk.dump(positions, out_file)
    out_file.close()
            
def moveToDefined():
    file_name = saved_position_select.get()
    with open(file_name, "rb") as input_file:
        saved_pos = pk.load(input_file)
    


# =============================================================================
# Create the drop-down menu and the drop-down buttons
# =============================================================================
menubar = tk.Menu(window)
# Create "File" menu button and all sub-buttons
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Close connection", command=closeConnection)
menubar.add_cascade(label="File", menu=filemenu)
# Create "Help" menu button and all sub-buttons
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=donothing)

window.config(menu=menubar)



# =============================================================================
# Create main frame to place the window widgets
# =============================================================================
mainframe = tk.Frame(window)
mainframe.grid(column=0, row=0, sticky=("N", "W", "E", "S"))

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)	


## Create Label frame containing the connection setup
connection_setup = tk.LabelFrame(mainframe, text="Connection Setup")
connection_setup.grid(column=0, row=0, pady=10, padx=10, columnspan=3)

port_desc = tk.Label(connection_setup, text="Port")
port_desc.grid(column=0, row=0, sticky=("N","W"), pady=10, padx=10)

port_select = ttk.Combobox(connection_setup, values=port_list)
port_select.grid(column=0, row=1, sticky=("N", "W"), pady=10, padx=10)
port_select.bind("<<ComboboxSelected>>", ComboboxPort)

baud_desc = tk.Label(connection_setup, text="Baudrate")
baud_desc.grid(column=1, row=0, sticky=("N","W"), pady=10, padx=10)

baud_var = tk.StringVar()
baud_value = tk.Entry(connection_setup, width=12,textvariable=baud_var, state="readonly")
baud_var.set(str(baudrate))
baud_value.grid(column=1, row=1, sticky=("N", "W"), pady=10, padx=10)

connect_button = tk.Button(connection_setup, text="Connect", command=connectToArduino)
connect_button.grid(column=2, row=1, sticky="W")

status_label = tk.Label(connection_setup, text="Status")
status_label.grid(column=3, row=0, sticky=("N","E"), pady=10, padx=65)


# Create connection status LED
status_led= tk.Canvas(connection_setup, height=20, width=20)
status_led.grid(column=3, row=1, sticky=("N","W"), pady=10, padx=75)

coord = 5,5,15,15
status_led.create_oval(coord, fill=status_colors[connection_status])


## Create label frame for the movement setup
movement_setup = tk.LabelFrame(mainframe, text="Movement")
movement_setup.grid(column=0, row=1, sticky=("N","W"), pady=10, padx=10)


# First entry for the base
base_label = tk.Label(movement_setup, text="Base")
base_label.grid(column=0, row=0, sticky=("W"), pady=10, padx=10)

base_slider = tk.Scale(movement_setup, from_=0, to=180,
                       orient ="horizontal", tickinterval=90, length=150)
base_slider.grid(column=1, row=0, sticky=("N","W"), pady=10, padx=10)

base_move_button = tk.Button(movement_setup, text="Move", 
                             command=singleMove_base)
base_move_button.grid(column=2, row=0, sticky=("W"), pady=10, padx=10)

# Second entry for the shoulder
shoulder_label = tk.Label(movement_setup, text="Shoulder")
shoulder_label.grid(column=0, row=1, sticky=("W"), pady=10, padx=10)

shoulder_slider = tk.Scale(movement_setup, from_=0, to=180,
                       orient ="horizontal", tickinterval=90, length=150)
shoulder_slider.grid(column=1, row=1, sticky=("N","W"), pady=10, padx=10)

shoulder_move_button = tk.Button(movement_setup, text="Move", 
                                 command=singleMove_shoulder)
shoulder_move_button.grid(column=2, row=1, sticky=("W"), pady=10, padx=10)

# Third entry for the elbow
elbow_label = tk.Label(movement_setup, text="Elbow")
elbow_label.grid(column=0, row=2, sticky=("W"), pady=10, padx=10)

elbow_slider = tk.Scale(movement_setup, from_=0, to=180,
                       orient ="horizontal", tickinterval=90, length=150)
elbow_slider.grid(column=1, row=2, sticky=("N","W"), pady=10, padx=10)

elbow_move_button = tk.Button(movement_setup, text="Move", command=singleMove_elbow)
elbow_move_button.grid(column=2, row=2, sticky=("W"), pady=10, padx=10)

# Fourth entry for the wrist
wrist_label = tk.Label(movement_setup, text="Wrist")
wrist_label.grid(column=0, row=3, sticky=("W"), pady=10, padx=10)

wrist_slider = tk.Scale(movement_setup, from_=0, to=180,
                       orient ="horizontal", tickinterval=90, length=150)
wrist_slider.grid(column=1, row=3, sticky=("N","W"), pady=10, padx=10)

wrist_move_button = tk.Button(movement_setup, text="Move", command=singleMove_wrist)
wrist_move_button.grid(column=2, row=3, sticky=("W"), pady=10, padx=10)

# Entry for the clamp controls
clamp_label = tk.Label(movement_setup, text="Clamp")
clamp_label.grid(column=0, row=4, sticky=("W"), pady=10, padx=10)

clamp_open_button = tk.Button(movement_setup, text="Open", command=openClamp)
clamp_open_button.grid(column=1, row=4, sticky=("E"), pady=10, padx=10)

clamp_close_button = tk.Button(movement_setup, text="Close", command=closeClamp)
clamp_close_button.grid(column=2, row=4, sticky=("W"), pady=10, padx=10)

## Create label frame for the programming setup
program_setup = tk.LabelFrame(mainframe, text="Programming")
program_setup.grid(column=2, row=1, sticky=("N","W"), pady=10, padx=10, columnspan=3)

# Label for the save
save_position_label = tk.Label(program_setup, text="Save current position as: ",
                               wraplength=100)
save_position_label.grid(column=0, row=0, sticky="W", pady=10, padx=10)

# text for the save position name
save_position_name = tk.Entry(program_setup)
save_position_name.grid(column=1, row=0, sticky="W", pady=10, padx=10)

# button for save name action
save_position_button = tk.Button(program_setup, text="Save", command=savePosition)
save_position_button.grid(column=2, row=0, sticky="W", pady=10, padx=10)

# Label for stored positions
saved_position_label = tk.Label(program_setup, text="Move to selected position",
                                wraplength=100)
saved_position_label.grid(column=0, row=1, sticky="W", pady=10, padx=10)

# list of saved positions
saved_position_select = ttk.Combobox(program_setup, values=saved_programs)
saved_position_select.grid(column=1, row=1, sticky="W", pady=10, padx=10)

# button to move to selected positions
move_position_button = tk.Button(program_setup, text="Go", command=donothing)
move_position_button.grid(column=2, row=1, sticky="W", pady=10, padx=10)

#text_debug = tk.Text(program_setup,height=2, width=10)
#text_debug.grid(column=0, row=2)
#text_debug.insert("end","Hey there")


window.mainloop()