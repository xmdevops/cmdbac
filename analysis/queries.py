#!/usr/bin/env python
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "core"))

import re
import csv
import numpy as np

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmudbac.settings")
import django
django.setup()

from library.models import *

NUM_BINS = 10

def query_stats():
    stats = {}

    for repo in Repository.objects.filter(latest_attempt__result = 'OK'):
        actions = Action.objects.filter(attempt = repo.latest_attempt)
        if len(actions) == 0:
            continue
        
        for action in actions:
            counters = Counter.objects.filter(action = action)
            for counter in counters:
                stats[counter.description] = stats.get(counter.description, 0) + counter.count
                stats['TOTAL'] = stats.get('TOTAL', 0) + counter.count

    print stats

def table_coverage_stats(directory = '.'):
    stats = []

    for repo in Repository.objects.filter(latest_attempt__result = 'OK'):
        actions = Action.objects.filter(attempt = repo.latest_attempt)
        if len(actions) == 0:
            continue

        statistics = Statistic.objects.filter(attempt = repo.latest_attempt)
        if len(statistics) == 0:
            continue
        statistic = statistics.get(description = 'num_tables')
        
        covered_tables = set()
        for action in actions:
            for query in Query.objects.filter(action = action):
                for table in re.findall('FROM\s*\S+', query.content.upper()):
                    table_name = table.replace('FROM', '').replace("'", "").replace(' ', '')
                    covered_tables.add(table_name)
               
        percentage = int(float(len(covered_tables) * 100) / statistic.count / 10)
        stats.append(percentage)

    hist, bin_edges = np.histogram(stats, NUM_BINS)
        
    with open(os.path.join(directory, 'table_coverage.csv'), 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for i in xrange(NUM_BINS):
            writer.writerow([int(bin_edges[i]), hist[i]])

def main():
    # query_stats()
    table_coverage_stats()

if __name__ == '__main__':
    main()
