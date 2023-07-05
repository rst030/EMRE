# mpl based
import matplotlib.pyplot as plt

class plotter():

    # fig, ax = plt.subplots()
    plt.title('multithreading plot')
    plt.xlabel('xlabel')
    plt.xlabel('ylabel')

    def __init__(self):
        plt.title('My first graph!')
        # function to show the plot
        plt.show(block=False)
        plt.pause(0.01)


    def replot(self,xdata,ydata):
        # clean up
        for artist in plt.gca().lines + plt.gca().collections:
            artist.remove()
        # update
        plt.plot(xdata, ydata, '--k')
        # release!
        plt.show(block=False)
        plt.pause(0.01)
        print(' --------------------------------- plt updates ---------------------------------')
