#!/usr/bin/env python

"""
Takes any number of files containing John The Ripper's
output and presents a chart showing the cummulative count of
passwords cracked or successful guesses (see below).

x axis - # of guesses
y axis - passwords cracked (with JtR's NoLoaderDupeCheck = Y)

Note: if NoLoaderDupeCheck = N, y axis is the # of successful guesses (unique passwords cracked)

The lines should be of the form

4175g 0:00:00:02 1512g/s 362358p/s 362358c/s 11086MC/s tnatupsi..tnerapdn

or for JtR older than 1.8:

guesses: 16479  time: 0:00:55:04  c/s: 210782M  trying: 1rolandu - onsmaribel

"""


import argparse
import re
import matplotlib.pyplot as plt
from pylab import *
import os
import palettable.colorbrewer.qualitative

markers = ['-','--','-.',':','+','x','*','.',',','v','o','^','<','>','1','2',\
    '3','4','s','p','h','H','D','d','|','_']


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--total', type=int, default=0,
        help='total count of passwords in the target. If this argument is not\
        passed, y axis will be the absolute count of passwords cracked, instead\
        of relative count (percentage).')
    parser.add_argument('-i', '--interval', type=int, default=0,
        help='subsample according to this interval')
    parser.add_argument('-s', '--scale', type=int, default=6,
        help='10^s. By default, the n-th status line represents the n*10^6th guess.')
    parser.add_argument('-l', '--location', type=int, default=2,
        help="location of the legend. see matplotlib\'s legend guide \
        http://matplotlib.org/users/legend_guide.html ")
    parser.add_argument('-c', '--cutoff', type=float, default=float('inf'),
        help='cut off the sample at a certain record')
    parser.add_argument('-o', '--old', action='store_true',
        help='old output format (before JtR 1.8)')
    parser.add_argument('files', nargs='+', type=file)
    parser.add_argument('--width', type=int, default=8,
        help="width. In inches!")
    parser.add_argument('--height', type=int, default=6,
        help="height. In inches!")
    parser.add_argument('--dpi', type=int, default=100,
        help="dpi (dots per inch) ")

    return parser.parse_args()

if __name__ == '__main__':
    opts = options()
    files = opts.files
    total_count = opts.total
    INTERVAL = opts.interval  # Number of records to skip. e.g., with INTERVAL = 4, we will use every 5th record.
    nFiles = len(files)
    scale = opts.scale

    if opts.old:
        regex = r'guesses: (\d+)'
    else:
        regex = r'^(\d+)g'

    # load an appropriate color palette from colorbrewer

    colors = getattr(palettable.colorbrewer.qualitative, \
        "Dark2_" + str(max(3,nFiles)) if nFiles < 9
        else "Paired_" + str(nFiles)).hex_colors

    figure(figsize=(opts.width, opts.height), dpi=opts.dpi)

    for n, f in enumerate(files):
        x_axis = []
        y_axis = []

        # for the case the log has output of sequential sessions
        # at some point "guesses" will restart from 0
        last_y = 0
        offset = 0

        i = 1
        interval_count = 0
        for line in f:

            # extract x and y values
            matches = re.findall(regex, line)
            if not matches: continue

            x = i
            y = int(matches[0])

            # checks for need of offset
            if y < last_y:
                offset += last_y


            # adds the data point if not in the interval
            interval_count += 1
            if interval_count >= INTERVAL + 1 or i == 1: # always use the 1st record.
                if i != 1: # if it's the 1st record, don't restart the count
                    interval_count = 0

                if total_count:
                    y_axis.append(float(y + offset)*100/total_count)
                else:
                    y_axis.append(y + offset)

                x_axis.append(x)

            if i == opts.cutoff:  # stops at cutoff value
                break

            i += 1
            last_y = y


        plt.plot(x_axis, y_axis, markers[0], label=os.path.basename(f.name)[:-4],
         color=colors[n], markersize= 4 if markers[n]=='x' else 6)

    if (total_count):
        ylabel('% of passwords guessed')
    else:
        ylabel('Passwords guessed')

    xlabel('Number of guesses ($10^{}$)'.format(scale))
    plt.legend(loc=opts.location)
    plt.grid(linewidth=1, linestyle='-', alpha=0.7, color='#EDEDED')

    # draw grid behind the lines
    ax = plt.subplot(111)
    ax.set_axisbelow(True)
    # ax.set_yscale('log', basey=2)
    # ax.set_ylim([0,max(y_axis)*1.1])

    plt.tight_layout()

    plt.savefig('chart.pdf', bbox_inches='tight', pad_inches=0)
    plt.savefig('chart.png', dpi=200, bbox_inches='tight', pad_inches=0)
    plt.show()
