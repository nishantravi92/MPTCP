 #! /usr/bin/env python2.7

import sys
import csv
import os


def print_map(my_map):
	for key in my_map:
		print key
		for line in my_map[key]:
			print line
		print '\n'

def create_map_from_file(file_name):
	cpu_map = dict()
	file = open(file_name, 'rb')
	csv_file = csv.reader(file)
	line_count = 0
	frequency = 0
	for line in csv_file:
		row = line_count%7
		if row == 0:
			frequency = int(line[1])
			cpu_map[frequency] = []
		elif row == 3 or row == 4 or row == 5 or row == 6:
			int_line = line[1:]
			int_line = [ float(x) for x in int_line ]
			cpu_map[frequency].append(int_line)
		line_count += 1
	cpu_map[0] = [[0, 0, 0, 0],
				  [0, 0, 0, 0],
				  [0, 0, 0, 0],
				  [0, 0, 0, 0]]
	return cpu_map


def find_cpu_usage(cpu_map, complete_line):
	line = complete_line.split(' ')
	cpu0 = cpu_map[int(line[5])][0][0]
	cpu1 = cpu_map[int(line[6])][1][0] - cpu_map[int(line[6])][0][0]
	if cpu1 < 0:
		cpu1 = 0
	cpu2 = cpu_map[int(line[7])][2][0] - cpu_map[int(line[7])][1][0]
	if cpu2 < 0:
		cpu2 = 0
	cpu3 = cpu_map[int(line[8])][3][0] - cpu_map[int(line[8])][2][0]
	if cpu3 < 0:
		cpu3 = 0
	baseline_cpu = cpu0 + cpu1 + cpu2 + cpu3
	cpu0_util = (cpu_map[int(line[5])][0][2] - cpu_map[int(line[5])][0][0])*float(line[1])/100
	cpu1_util = (cpu_map[int(line[6])][1][2] - cpu_map[int(line[6])][1][0])*float(line[2])/(2*100)
	cpu2_util = (cpu_map[int(line[7])][2][2] - cpu_map[int(line[7])][2][0])*float(line[3])/(3*100)
	cpu3_util = (cpu_map[int(line[8])][3][2] - cpu_map[int(line[8])][3][0])*float(line[4])/(4*100)
	cpu_util_part = cpu0_util + cpu1_util + cpu2_util + cpu3_util
	#print "Baseline CPU:" + str(baseline_cpu) + " Utilization Part" + str(cpu_util_part) 
	return baseline_cpu + cpu_util_part   

def find_average_from_cpu_file(cpu_path):
	mtime = lambda f: os.stat(os.path.join(cpu_path, f)).st_mtime
	files = list(sorted(os.listdir(cpu_path)))
	for i in range(0, len(files)):
		files[i] = cpu_path + files[i]
	for file in files:
		print file
		average = 0
		with open(file) as f:
			lines = f.readlines()
			num_of_lines = 0
			for i in range(1, len(lines)):
				data = lines[i].split(' ')
				if len(data) != 9:
					continue
				average += find_cpu_usage(cpu_map, lines[i])
				num_of_lines += 1

			average /= num_of_lines
			print average



cpu_map = create_map_from_file(sys.argv[1])
find_average_from_cpu_file(sys.argv[2])
#print find_cpu_usage(cpu_map, "04:33:09 100 100 100 100 1958400 1958400 1958400 1958400")