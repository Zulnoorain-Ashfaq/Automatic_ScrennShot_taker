import os
import time
from PIL import ImageChops, ImageGrab
import pickle
from make_structured_screenshots import make_structured_images
import numpy
import threading
from tkinter import Tk, Button, StringVar, Entry, Label
import pyautogui
import matplotlib.pyplot as plt
from pynput.keyboard import Listener
from pynput.keyboard._win32 import Key
import datetime
from pynput import mouse
from functools import partial

# pyautogui uses ImageGrab in backend we use partial function to edit its call to all screens

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

# default screen size
DEFAULT_X = 1920
DEFAULT_Y = 1080
# getting difference so that it can work with multiple displays
screen_size = pyautogui.screenshot().size
DIFFERENCE_IN_X = screen_size[0] - DEFAULT_X
DIFFERENCE_IN_Y = screen_size[1] - DEFAULT_Y
print(DIFFERENCE_IN_X)

# initializing variables
# auto_condition is used for taking screenshot of the region when ever the screen changes
auto_condition = False

# path where screenshots will be saved
PATH = "screenshots/path"
# path to the folder containing necessary files for program
FILES_PATH = "../data"


def key_click(key, *args):
    """
    this is function which reads keyboard input and perform necessary actions
    :param key: input_key
    :param args:
    :return: None

    ` key           :       is used for taking screenshots manually
    page_up key     :       is used to toggle auto mode
    page_down key   :       is used to check the status of the program if it is running in auto mode or not
    home key        :       is used to update the name of the course and the locations of the selected region
    end key         :       is used to close the program, and it will sort the screenshot in their suitable folders

    """
    global locations, course_name, auto_condition, thread, PATH
    if str(key) == "'`'":
        # setting file name to current date and time plus the course name
        file_name = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S-") + course_name
        # taking screenshot of the required region
        pyautogui.screenshot(PATH + file_name + ".png", region=locations)
    elif key == Key.page_up:
        # toggling the auto-mode
        if auto_condition:
            auto_condition = False
            # waiting for the thread to join
            thread.join()

            # making a pop-up window to show the status of auto mode
            tp = Tk()
            tp.geometry("300x100")
            Label(tp, text="    Auto-mode Disabled").place(x=20, y=25)
            but = Button(
                tp,
                text="   OK   ",
                activebackground="red",
                activeforeground="blue",
                command=partial(on_press, tp),
            )
            but.place(x=140, y=65)
            but.focus_force()
            tp.mainloop()
        else:
            # enabling auto mode
            auto_condition = True
            tp = Tk()
            tp.geometry("300x100")
            Label(tp, text="    Auto-mode enabled").place(x=20, y=25)
            but = Button(
                tp,
                text="   OK   ",
                activebackground="red",
                activeforeground="blue",
                command=partial(on_press, tp),
            )
            but.place(x=140, y=65)
            but.focus_force()
            tp.mainloop()
            thread = threading.Thread(target=auto_mode)
            thread.start()

    elif key == Key.page_down:
        # displaying status of the program
        tp = Tk()
        tp.geometry("300x100")
        Label(tp, text=f"Program = True  AutoMode = {auto_condition}").place(x=20, y=25)
        tp.title(course_name)
        but = Button(
            tp,
            text="   OK   ",
            activebackground="red",
            activeforeground="blue",
            command=partial(on_press, tp),
        )
        but.place(x=140, y=65)
        but.focus_force()
        tp.mainloop()

    elif key == Key.home:
        # updating course name and locations
        print("getting new Locations")
        locations = get_location()
    elif key == Key.end:
        # ending the program and making structured screenshots
        make_structured_images(
            "D://Programming/SCREENSHOTS", "D://Programming/STRUCTURED_SCREENSHOTS"
        )
        quit()


def auto_mode():
    """
    this function is used to take screenshots automatically when the screen changes this is very helpful in watching a
    tutorial or something like that.
    :return:
    """
    global auto_condition, locations, PATH
    frame_1 = pyautogui.screenshot(region=locations)
    while auto_condition:
        frame_2 = pyautogui.screenshot(region=locations)
        # noinspection PyTypeChecker
        difference = numpy.asarray(ImageChops.difference(frame_1, frame_2))
        if difference.mean() > 0.2:
            file_name = (
                datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S-") + course_name
            )
            pyautogui.screenshot(PATH + file_name + ".png", region=locations)
            time.sleep(0.3)
        frame_1 = frame_2.copy()


def on_press(top):
    top.destroy()
    top.quit()


def single_d(top):
    """
    this a single display function which will use the previous locations if they are present else it will take new
    location and save them for later use
    :param top: tkinter window
    :return:
    """
    global called_from
    # loading locations
    try:
        loc = pickle.load(open(f"{FILES_PATH}/single.pkl", "rb"))
    except:
        loc = []
        called_from = f"{FILES_PATH}/single.pkl"
    locations.extend(loc)
    top.destroy()
    top.quit()


def multi_d(top):
    """
    this a multi display function which will use the previous locations if they are present else it will take new
    location and save them for later use
    :param top: tkinter window
    :return:
    """
    global called_from
    # loading locations
    try:
        loc = pickle.load(open(f"{FILES_PATH}/multi.pkl", "rb"))
    except:
        loc = []
        called_from = f"{FILES_PATH}/multi.pkl"
    locations.extend(loc)
    top.destroy()
    top.quit()


def reset(top):
    """
    it will reset all the saved locations
    :param top:tkinter window
    :return:
    """
    global called_from
    try:
        os.remove(f"{FILES_PATH}/single.pkl")
    except:
        pass
    try:
        os.remove(f"{FILES_PATH}/multi.pkl")
    except:
        pass
    called_from = "reset"
    top.destroy()
    top.quit()


def get_location():
    """
    it gets the location coordinates of the screen and the course name/ screenshot name
    :return:
    """
    global course_name, locations, called_from
    called_from = ""
    locations = []

    top = Tk()
    top.geometry("300x100")

    course_var = StringVar()
    get_course_name = partial(on_press, top)
    single_d_ = partial(single_d, top)
    multi_d_ = partial(multi_d, top)
    reset_ = partial(reset, top)

    Label(top, text="Course Name:").place(x=20, y=25)

    inpu = Entry(top, textvariable=course_var)
    inpu.place(x=110, y=25)
    Button(
        top,
        text="Submit",
        activebackground="red",
        activeforeground="blue",
        command=get_course_name,
    ).place(x=240, y=65)
    Button(
        top,
        text="Reset",
        activebackground="red",
        activeforeground="blue",
        command=reset_,
    ).place(x=10, y=65)
    Button(
        top,
        text="Multi-D",
        activebackground="red",
        activeforeground="blue",
        command=multi_d_,
    ).place(x=80, y=65)
    Button(
        top,
        text="Single-D",
        activebackground="red",
        activeforeground="blue",
        command=single_d_,
    ).place(x=150, y=65)

    top.mainloop()
    if called_from == "reset":
        raise ValueError

    # getting course name
    course_name = course_var.get()
    # course_name = simpledialog.askstring(
    #     title="course_name", prompt="Enter course name:"
    # )
    # if the course name is empty then setting it to the title of the active window
    if course_name == "":
        course_name = pyautogui.getActiveWindow().title
    # removing illegal chars form the title
    illegal_chars = ["\\", "/", "*", "?", ":", "|"]
    for char in illegal_chars:
        course_name = course_name.replace(char, "_")

    # getting locations form the user
    number = [0]
    if locations:
        return locations

    def on_click(x, y, button, pressed):
        # adding the difference for multiple screens
        x += DIFFERENCE_IN_X
        y += DIFFERENCE_IN_Y
        if not pressed and number[0] >= 2:
            # Stop listener
            return False
        if pressed:
            if number[0] == 1:
                locations.extend([x - locations[0], y - locations[1]])
            else:
                locations.extend([x, y])
            number[0] += 1

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
    if called_from:
        pickle.dump(locations, open(called_from, "wb"))
    return locations


# getting locations of screen
locations = get_location()
# taking sample screenshot and showing it to the user
picture = pyautogui.screenshot(region=locations)
plt.title(course_name)
plt.imshow(picture)
plt.show()

# continuously listening the keyboard
with Listener(on_press=key_click) as listener:
    listener.join()
