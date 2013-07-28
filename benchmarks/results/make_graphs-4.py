#!/usr/bin/env python

import matplotlib
import pylab as plt
import numpy as np

import os
import sys
import math

def filter_name(results, name):
  def match(ent):
    return ent[0]['name'] == name
  return [x for x in results if match(x)]

def order_results_by_threads(results):
  # res is list[(config, results)], change to
  # list[(num_threads, results)]
  def trfm(ent):
    return (ent[0]['threads'], ent[1])
  return map(trfm, results)

def split_results_by_predicate(results, pred):
  s0, s1 = [], []
  for res in results:
    if pred(res):
      s0.append(res)
    else:
      s1.append(res)
  return s0, s1

def extract_result_position(k, res):
  if type(res) == list:
    return [x[k] for x in res]
  return res[k]

def extract_throughput(results, persist):
  def trfm(ent):
    return (ent[0], extract_result_position(0 if not persist else 1, ent[1]))
  return map(trfm, results)

def extract_latency(results, persist):
  def trfm(ent):
    return (ent[0], extract_result_position(2 if not persist else 3, ent[1]))
  return map(trfm, results)

def XX(x):
  return [e[0] for e in x]

def median(x): return x[len(x)/2]

def YY(x, agger=median):
  def checked(e):
    if type(e) == list:
      return agger(e)
    return e
  return [checked(e[1]) for e in x]

def handle_scale_tpcc(f, results):
  # two graphs
  # x-axis is num threads on both
  # y-axis[0] is throughput
  # y-axis[1] is latency

  data_by_threads = order_results_by_threads(results)
  no_persist, with_persist = \
      split_results_by_predicate(results, lambda x: not x[0]['persist'])
  no_persist, with_persist = \
      order_results_by_threads(no_persist), order_results_by_threads(with_persist)

  no_persist_throughput, no_persist_latency = \
      extract_throughput(no_persist, False), extract_latency(no_persist, False)
  with_persist_throughput, with_persist_latency = \
      extract_throughput(with_persist, True), extract_latency(with_persist, True)

  fig = plt.figure()
  ax = plt.subplot(111)
  ax.plot(XX(no_persist_throughput), YY(no_persist_throughput))
  ax.plot(XX(with_persist_throughput), YY(with_persist_throughput))
  ax.legend(('No-Persist', 'Persist'), loc='upper left')
  ax.set_xlabel('threads')
  ax.set_ylabel('throughput (txns/sec)')
  bname = '.'.join(os.path.basename(f).split('.')[:-1])
  fig.savefig('.'.join([bname + '-scale_tpcc-throughput', 'pdf']))

  fig = plt.figure()
  ax = plt.subplot(111)
  ax.plot(XX(no_persist_latency), YY(no_persist_latency))
  ax.plot(XX(with_persist_latency), YY(with_persist_latency))
  ax.legend(('No-Persist', 'Persist'), loc='upper left')
  ax.set_xlabel('threads')
  ax.set_ylabel('latency (ms/txn)')
  bname = '.'.join(os.path.basename(f).split('.')[:-1])
  fig.savefig('.'.join([bname + '-scale_tpcc-latency', 'pdf']))

if __name__ == '__main__':
  files = sys.argv[1:]
  for f in files:
    execfile(f)

    # scale_tpcc
    scale_tpcc = filter_name(RESULTS, 'scale_tpcc')
    if scale_tpcc:
      handle_scale_tpcc(f, scale_tpcc)
