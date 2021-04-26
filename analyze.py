#import sys
#from PIL import Image
#import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DFT_WIDTH = 1024


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

    image1d_dfts = []
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

        # make a DFT of the points
        image1d = np.zeros(DFT_WIDTH)
        for index, row in df.iterrows():
            image1d[min(int(row[0]*DFT_WIDTH), DFT_WIDTH-1)] = 1;
        image1d_dft = np.fft.fft(image1d)
        image1d_dft = np.fft.fftshift(image1d_dft)
        image1d_dft = np.abs(image1d_dft)
        image1d_dft2 = np.log(1+image1d_dft)
        if first:
            plt.plot(image1d_dft2)
            plt.title("Single DFT of " + titles[fileGroup])
            plt.savefig(fileName[:len(fileName) - 4] + ".dft.png")
            plt.close(plt.gcf())

        image1d_dfts.append(image1d_dft)

        # TODO: better dft graph!

        # make a DFT of the difference between points
        df_diff = np.diff(df, axis=0)
        df_diff_dft = np.fft.fft(df_diff)
        df_diff_dft = np.fft.fftshift(df_diff_dft)
        df_diff_dft = np.abs(df_diff_dft)
        df_diff_dft2 = np.log(1+df_diff_dft)
        if first:
            plt.plot(df_diff_dft2)
            plt.title("Single DFT of Distances For " + titles[fileGroup])
            plt.savefig(fileName[:len(fileName) - 4] + ".diffdft.png")
            plt.close(plt.gcf())

        diff_dfts.append(df_diff_dft)
        
        # clear out the first variable
        if first:
            first = False

        #quit()

    # Make averaged DFT for file group
    avg = diff_dfts[0] / len(diff_dfts)
    for x in range(len(diff_dfts)-1):
        avg = avg + diff_dfts[x+1] / len(diff_dfts)

    # graph the averaged DFT
    # TODO: better DFT graph!
    plt.plot(np.log(1+avg))
    plt.title("Averaged DFT of Distances For " + titles[fileGroup])
    plt.savefig("out/"+fileGroup+".avg.diffdft.png")
    plt.close(plt.gcf())


    # Make averaged DFT for file group
    avg = image1d_dfts[0] / len(image1d_dfts)
    for x in range(len(image1d_dfts)-1):
        avg = avg + image1d_dfts[x+1] / len(image1d_dfts)

    # graph the averaged DFT
    # TODO: better DFT graph!
    plt.plot(np.log(1+avg))
    plt.title("Averaged DFT of " + titles[fileGroup])
    plt.savefig("out/"+fileGroup+".avg.dft.png")
    plt.close(plt.gcf())
