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

# TODO: better dft graph!
def SaveDFT(data_dft, fileName, title):
    data_dft2 = np.log(1+data_dft)
    plt.plot(data_dft2)
    plt.title(title)
    plt.savefig(fileName)
    plt.close(plt.gcf())

def MakeDFT(data):
    data_dft = np.fft.fft(data)
    #data_dft[0] = 0 # zero out dc
    data_dft = np.fft.fftshift(data_dft)
    data_dft = np.abs(data_dft)
    return data_dft

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
        image1d_dft = MakeDFT(image1d)
        if first:
            SaveDFT(image1d_dft, fileName[:len(fileName) - 4] + ".dft.png", "Single DFT of " + titles[fileGroup])
        image1d_dfts.append(image1d_dft)

        # make a DFT of the difference between points
        df_diff = np.diff(df, axis=0)
        df_diff_dft = MakeDFT(df_diff)
        if first:
            SaveDFT(df_diff_dft, fileName[:len(fileName) - 4] + ".diffdft.png", "Single DFT of Distances For " + titles[fileGroup])
        diff_dfts.append(df_diff_dft)
        
        # clear out the first variable
        if first:
            first = False

        #quit()
            # TODO: keep converting the DFT functions

    # Make averaged diff DFT for file group
    avg = diff_dfts[0] / len(diff_dfts)
    for x in range(len(diff_dfts)-1):
        avg = avg + diff_dfts[x+1] / len(diff_dfts)

    # Save the averaged diff DFT
    SaveDFT(avg, "out/"+fileGroup+".avg.diffdft.png", "Averaged DFT of Distances For " + titles[fileGroup])

    # Make averaged DFT for file group
    avg = image1d_dfts[0] / len(image1d_dfts)
    for x in range(len(image1d_dfts)-1):
        avg = avg + image1d_dfts[x+1] / len(image1d_dfts)

    # Save the averaged DFT
    SaveDFT(avg, "out/"+fileGroup+".avg.dft.png", "Averaged DFT of " + titles[fileGroup])
