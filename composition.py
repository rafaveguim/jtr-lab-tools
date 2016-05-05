#!/usr/bin/env python

import argparse
import re
import seaborn as sea
import numpy as np
import pandas as pd
import math
import os

#colors = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']
colors = ['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E', '#E6AB02', '#A6761D', '#666666']

policies = []

class Policy:
    """A composition policy."""
    def __init__(self, name, min_length, min_alpha, min_symbols, min_digits, min_capital):
        self.name        = name
        self.min_length  = min_length
        self.min_alpha   = min_alpha
        self.min_symbols = min_symbols
        self.min_digits  = min_digits
        self.min_capital = min_capital

    def isCompliant(self, password):
        return len(password) >= self.min_length \
            and len(re.findall('\d', password)) >= self.min_digits \
            and len(re.findall('[A-Za-z]', password)) >= self.min_alpha \
            and len(re.findall('[^a-zA-Z0-9\s]', password)) >= self.min_symbols \
            and len(re.findall('[A-Z]', password)) >= self.min_capital

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--ref', type=file, help='a reference file containing all plain text passwords')
    parser.add_argument('files', nargs='+', type=file, help='password files')
    parser.add_argument('-r', '--relative', action='store_true', help='toggle height of the bar as relative count')
    parser.add_argument('-p', '--policies', nargs='+', help='minimum acceptable passwords' +
        ' under each composition policy considered (e.g., Abcdef1 -> 7 chars, 1 capital, 1 number)')
    return parser.parse_args()

def parse_policies(instances):
    """Infers the underlying password policies of a list of password examples.
       Return: a list of Policy instances.
    """
    policies = []
    for instance in instances:
        min_length  = len(instance)
        min_alpha   = len(re.findall('[a-z]', instance))
        min_digits  = len(re.findall('\d', instance))
        min_symbols = len(re.findall('%', instance))
        min_capital = len(re.findall('[A-Z]', instance))
        p = Policy(instance, min_length, min_alpha, min_symbols, min_digits, min_capital)
        policies.append(p)
    return policies

def countPerPolicy(f, policies):
    """ Counts the number of passwords compliant with each of the policies.
    Return: an array of counts, one slot per policy.
    """
    counts = np.zeros(shape=(len(policies)), dtype=int)
    for line in f:
        pwd = line.rstrip().split(':')[1]
        for i, policy in enumerate(policies):
            counts[i] += policy.isCompliant(pwd)
    return counts

def chart(df):
    ax = sea.barplot(y="passwords", x="policy", hue="collection", data=df)
    ax.set(ylabel='matches')
    sea.plt.savefig("composition.png", dpi=200)
    sea.plt.show()


if __name__ == "__main__":
    opts = options()
    policy_examples = opts.policies
    policies = parse_policies(policy_examples)
    nrows = len(policies)*len(opts.files)
    npolicies = len(policies)
    # create a table-like dictionary (long form)
    data = {'collection': np.ndarray(shape=(nrows), dtype=object), \
            'policy':     np.ndarray(shape=(nrows), dtype=object), \
            'passwords':  np.ndarray(shape=(nrows), dtype=int)}
    for i, f in enumerate(opts.files):
        filename = os.path.splitext(os.path.split(f.name)[1])[0]
        s_index = i * npolicies
        e_index = s_index + npolicies
        data['collection'][s_index:e_index] = filename
        data['policy']    [s_index:e_index] = policy_examples
        data['passwords'] [s_index:e_index] = countPerPolicy(f, policies)
    # transform data into a nice Pandas DataFrame
    print data
    df = pd.DataFrame(data)
    print df
    chart(df)
