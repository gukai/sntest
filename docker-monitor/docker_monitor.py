#!/usr/bin/python

#-*- coding: utf-8 -*-
#author:Deng Lei
#email: dl528888@gmail.com
from docker import Client
import sys
import os
import socket, struct, fcntl
import re
import multiprocessing
import subprocess
import time
import ast
import json
import websocket

def check_container_stats(container_name,collect_item):
  container_collect=docker_client.stats(container_name)
  old_result=json.loads(container_collect.next())
  new_result=json.loads(container_collect.next())

  #print json.dumps(old_result, indent=2)
  #print json.dumps(new_result, indent=2)
  #print '>>>', collect_item
  container_collect.close()
  if collect_item == 'cpu_total_usage':
    result=new_result['cpu_stats']['cpu_usage']['total_usage'] - old_result['cpu_stats']['cpu_usage']['total_usage']
  elif collect_item == 'cpu_system_usage':
    result=new_result['cpu_stats']['system_cpu_usage'] - old_result['cpu_stats']['system_cpu_usage']
  elif collect_item == 'cpu_percent':
    cpu_total_usage=new_result['cpu_stats']['cpu_usage']['total_usage'] - old_result['cpu_stats']['cpu_usage']['total_usage']
    cpu_system_uasge=new_result['cpu_stats']['system_cpu_usage'] - old_result['cpu_stats']['system_cpu_usage']
    cpu_num=len(old_result['cpu_stats']['cpu_usage']['percpu_usage'])
    result=round((float(cpu_total_usage)/float(cpu_system_uasge))*cpu_num*100.0,2)
  elif collect_item == 'mem_usage':
    result=new_result['memory_stats']['usage']
  elif collect_item == 'mem_limit':
    result=new_result['memory_stats']['limit']
  elif collect_item == 'mem_percent':
    mem_usage=new_result['memory_stats']['usage']
    mem_limit=new_result['memory_stats']['limit']
    result=round(float(mem_usage)/float(mem_limit)*100.0,2)
  #network_rx_packets=new_result['network']['rx_packets']
  #network_tx_packets=new_result['network']['tx_packets']
  elif collect_item == 'disk_percent':
#    disk_use_percent_command="docker exec %s  df -h |grep rootfs |awk '{print $5}' |awk -F '%' '{print $1}'"%container_name
#    print disk_use_percent_command
#    result=(subprocess.Popen(disk_use_percent_command,shell=True,stdout=subprocess.PIPE).stdout.readlines()[0]).strip('\n')
#    result=disk_use_percent
    disk_use_percent_command="docker exec %s df -h |grep rootfs |awk '{print $5}'"%container_name
    disk_use_percent=(subprocess.Popen(disk_use_percent_command,shell=True,stdout=subprocess.PIPE).stdout.readlines()[0]).strip('\n')
    result=disk_use_percent.split('%')[0]
  elif collect_item == 'network_rx_bytes':
    network_check_command="""docker exec %s ifconfig eth0|grep bytes|awk -F ':' '{print $2,$3}'|awk -F '(' '{print $1,$2}'|awk -F ')' '{print $1}'|awk '{print "{\\"rx\\":"$1",\\"tx\\":"$2"}"}'"""%container_name
    network_old_result=json.loads(((subprocess.Popen(network_check_command,shell=True,stdout=subprocess.PIPE)).stdout.readlines()[0]).strip('\n'))
    time.sleep(1)
    network_new_result=json.loads(((subprocess.Popen(network_check_command,shell=True,stdout=subprocess.PIPE)).stdout.readlines()[0]).strip('\n'))
    #unit KB
    result=int(network_new_result['rx']) - int(network_old_result['rx'])
  elif collect_item == 'network_tx_bytes':
    network_check_command="""docker exec %s ifconfig eth0|grep bytes|awk -F ':' '{print $2,$3}'|awk -F '(' '{print $1,$2}'|awk -F ')' '{print $1}'|awk '{print "{\\"rx\\":"$1",\\"tx\\":"$2"}"}'"""%container_name
    network_old_result=json.loads(((subprocess.Popen(network_check_command,shell=True,stdout=subprocess.PIPE)).stdout.readlines()[0]).strip('\n'))
    time.sleep(1)
    network_new_result=json.loads(((subprocess.Popen(network_check_command,shell=True,stdout=subprocess.PIPE)).stdout.readlines()[0]).strip('\n'))
    result=int(network_new_result['tx']) - int(network_old_result['tx'])
  return result

if __name__ == "__main__":
  docker_client = Client(base_url='unix://var/run/docker.sock', version='1.17')
  container_name=sys.argv[1]
  collect_item=sys.argv[2]
  print check_container_stats(container_name,collect_item)

