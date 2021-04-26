#import sys
#from PIL import Image
#import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


fileGroups = ["blue", "regular", "stratified", "white", "goldenratio", "antithetic"]

titles = {
    "blue":"Blue Noise Samples",
    "regular": "Regular Spaced Samples",
    "stratified": "Stratified Samples",
    "white": "Uniform Random Samples",
    "goldenratio": "Golden Ratio LDS",
    "antithetic": "Antithetic Uniform Random Samples",
    }

for fileGroup in fileGroups:
    first = True

    diff_dfts = []
    
    for fileName in glob.glob("out/" + fileGroup + "_*.csv"):
        df = pd.read_csv(fileName)
        print(fileName)

        # make a representative numberline image
        if first:
            # set up the figure
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlim(0,10)
            ax.set_ylim(0,10)

            # draw lines
            xmin = 1
            xmax = 9
            y = 5
            height = 1
            plt.hlines(y, xmin, xmax)
            plt.vlines(xmin, y - height / 2., y + height / 2.)
            plt.vlines(xmax, y - height / 2., y + height / 2.)

            # draw a point on the line
            for index, row in df.iterrows():
                plt.plot(row[0] * (xmax-xmin)+xmin,y, 'bo', ms = 5, mfc = 'b')

            # add an arrow
            #plt.annotate('Price five days ago', (px,y), xytext = (px - 1, y + 1), 
            #              arrowprops=dict(facecolor='black', shrink=0.1), 
            #              horizontalalignment='right')

            # add numbers
            plt.text(xmin - 0.1, y, '0', horizontalalignment='right')
            plt.text(xmax + 0.1, y, '1', horizontalalignment='left')
            plt.axis('off')
            plt.title(titles[fileGroup])
            plt.savefig(fileName[:len(fileName) - 4] + ".numberline.png")
            plt.close(plt.gcf())

        # TODO: dft of points. make a discretized 1d array that has a 1 where there is a point and 0 elsewhere, dft it. make 1d graph.

        # get the difference and make a dft of it
        df_diff = np.diff(df, axis=0)
        df_diff_dft = np.fft.fft(df_diff)
        df_diff_dft = np.fft.fftshift(df_diff_dft)
        df_diff_dft = np.log(1+np.abs(df_diff_dft))

        #TODO: i saw some other nice looking DFT graphs
        if first:
            plt.plot(df_diff_dft)
            plt.title("Single DFT of Distances For " + titles[fileGroup])
            plt.savefig(fileName[:len(fileName) - 4] + ".diffdft.png")
            plt.close(plt.gcf())

        diff_dfts.append(df_diff_dft)
        
        # clear out the first variable
        if first:
            first = False

        #quit()

    # TODO: make averaged DFT for fileGroup
    avg = diff_dfts[0] / len(diff_dfts)
    for x in range(len(diff_dfts)-1):
        avg = avg + diff_dfts[x+1] / len(diff_dfts)

    # graph the averaged DFT
    # TODO: better DFT graph!
    plt.plot(avg)
    plt.title("Averaged DFT of Distances For " + titles[fileGroup])
    plt.savefig("out/"+fileGroup+".avg.diffdft.png")
    plt.close(plt.gcf())


