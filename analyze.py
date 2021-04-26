import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DFT_WIDTH = 256


fileGroups = ["blue", "regular", "stratified", "white", "goldenratio", "antithetic"]

titles = {
    "blue":"Blue Noise Samples",
    "regular": "Regular Spaced Samples",
    "stratified": "Stratified Samples",
    "white": "Uniform Random Samples",
    "goldenratio": "Golden Ratio LDS",
    "antithetic": "Antithetic Uniform Random Samples",
    }

def SaveDFT(data_dft, fileName, title):
    freq = np.fft.fftfreq(len(data_dft))
    freq = np.fft.fftshift(freq)
    data_dft2 = np.log(1+data_dft)
    plt.plot(freq, data_dft2)
    plt.title(title)

    smallest = min(data_dft2)
    biggest = max(data_dft2)
    if biggest - smallest < 0.001:
        biggest = smallest + 0.001
    diff = biggest - smallest;
    smallest -= diff * 0.1
    biggest += diff * 0.1
    plt.ylim(smallest, biggest)
    
    plt.savefig(fileName)
    plt.close(plt.gcf())
    
def MakeDFT(data):
    data_dft = np.fft.fft(data)
    data_dft = np.fft.fftshift(data_dft)
    data_dft = np.abs(data_dft)
    return data_dft

def Lerp(a, b, t):
    return a*(1-t)+b*t

for fileGroup in fileGroups:
    fileIndex = 0

    image1d_dfts = []
    diff_dfts = []
    diff_histograms = []
    
    for fileName in glob.glob("out/" + fileGroup + "_*.csv"):
        df = pd.read_csv(fileName)
        print(fileName)

        # make a representative numberline image
        if fileIndex < 1:
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
        image1d_dfts.append(image1d_dft.copy())
        if fileIndex < 1:
            SaveDFT(image1d_dft, fileName[:len(fileName) - 4] + ".dft.png", "Single DFT of " + titles[fileGroup])

        # make a DFT of the difference between points
        df_diff = np.diff(df, axis=0)
        df_diff_dft = MakeDFT(df_diff)
        diff_dfts.append(df_diff_dft.copy())
        if fileIndex < 1:
            SaveDFT(df_diff_dft, fileName[:len(fileName) - 4] + ".diffdft.png", "Single DFT of Distances For " + titles[fileGroup])

        # make a histogram of the difference between points
        if fileIndex < 1:
            bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            hist, bin_edges = np.histogram(df_diff * len(df_diff), bins=bins)
            plt.bar(bin_edges[:-1], hist, width=0.1)
            plt.xlim(left=0)
            plt.title("Histogram of Distances For " + titles[fileGroup])
            plt.savefig(fileName[:len(fileName) - 4] + ".histogram.png")
            plt.close(plt.gcf())
            diff_histograms.append(hist.copy())
                    
        fileIndex = fileIndex + 1

    # Make averaged DFT for file group
    avg = image1d_dfts[0]
    for x in range(len(image1d_dfts)-1):
        avg = Lerp(avg, image1d_dfts[x+1], 1.0 / float(x+2))

    # Save the averaged DFT
    SaveDFT(avg, "out/"+fileGroup+".avg.dft.png", "Averaged DFT of " + titles[fileGroup])

    # Make averaged diff DFT for file group
    avg = diff_dfts[0] / len(diff_dfts)
    for x in range(len(diff_dfts)-1):
        avg = Lerp(avg, diff_dfts[x+1], 1.0 / float(x+2))

    # Save the averaged diff DFT
    SaveDFT(avg, "out/"+fileGroup+".avg.diffdft.png", "Averaged DFT of Distances For " + titles[fileGroup])

    # Make averaged histogram for file group
    avg = diff_histograms[0]
    for x in range(len(diff_histograms)-1):
        avg = Lerp(avg, diff_histograms[x+1], 1.0 / float(x+2))

    bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    hist, bin_edges = np.histogram(df_diff * len(df_diff), bins=bins)
    plt.bar(bin_edges[:-1], hist, width=0.1)
    plt.xlim(left=0)
    plt.title("Averaged Histogram of Distances For " + titles[fileGroup])
    plt.savefig("out/" + fileGroup + ".avg.histogram.png")
    plt.close(plt.gcf())
