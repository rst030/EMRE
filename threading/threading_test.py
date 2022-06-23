from multiprocessing import Process
import plotting_GUI # graphical user interface. buttons and all that.
import setup_scan # gui for setting up cw scan
import main_gui
from tkinter import Tk


def start_gui():
    gui_one = plotting_GUI.start_plotter_gui() # starting new gui instance

def start_scan():
    mg = main_gui.main_gui()

if __name__ == "__main__":

    Process(target=start_scan).start()

