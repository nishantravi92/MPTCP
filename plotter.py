import os
import sys
import numpy as np
from socket import inet_ntop, ntohs
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import datetime


def print_matrix(matrix):
	for i in range(0, len(matrix)):
		for j in range(0, len(matrix[i])):
			print matrix[i][j],
		print ''

def generate_plot(values, y_axis_label, filename):
	interfaces = ['WiFi', 'LTE', 'MP-WiFi', 'MP-LTE']
	N = len(values[0]) 
	space = 0.6 #the space between each set of bars
	width = (1 - space+0.2) / (N) #the width of the bars
	x_labels = interfaces[:]

	interface_averages = []
	interfaces_sd = []
	yerr = []
	for i in range(4):
		average = np.average(values[i])
		std = np.std(values[i]) 
		interface_averages.append(average)
		interfaces_sd.append(std)
		yerr.append(std)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	pos = [j - (1 - space) / 2. + 0 * width for j in range(1,N+1)]
	wifi = ax.bar(pos, values[0], width, color = 'white', hatch = '//', label = interfaces, yerr = yerr[0])
	pos = [j - (1 - space) / 2. + 1 * width for j in range(1,N+1)]
	lte = ax.bar(pos, values[1], width, color = 'white', hatch = 'X', label = interfaces, yerr = yerr[1])
	pos = [j - (1 - space) / 2. + 2 * width for j in range(1,N+1)]
	mpwifi = ax.bar(pos, values[2], width, color = 'white', hatch = '\\\\', label = interfaces, yerr = yerr[2])
	pos = [j - (1 - space) / 2. + 3 * width for j in range(1,N+1)]	
	mplte = ax.bar(pos, values[3], width, color = 'white', hatch = '||', label = interfaces, yerr = yerr[3])


	ax.legend((wifi[0], lte[0], mpwifi[0], mplte[0]), ('Core 0', 'Core 1', 'Core 2', 'Core 3'), bbox_to_anchor=(0., 1.07, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.1)

	

	ax.set_xticklabels(x_labels)
	ax.set_xticks(range(1, 5))
	#ax.set_xlabel("Interfaces")
	ax.set_ylabel(y_axis_label)
	ax.set_ylim([0, 1])
	plt.savefig(filename, bbox_inches='tight')		
	print "Generated plot: ",filename
	plt.close()

#Creates a matrix of required dimension m x n
def create_matrix(m, n):
	matrix = []
	for i in range(0, m):
		matrix.append([])
		for j in range(0, n):
			matrix[i].append(0)
	return matrix

# Returns a timedelta object
def convert_time_stamps_with_starting_time(time_stamp, start_time):
	return datetime.strptime(time_stamp, "%H:%M:%S.%f") - datetime.strptime(start_time, "%H:%M:%S.%f")

def time_in_between(absolute_time, start_and_end_time):
	start_time = int(start_and_end_time[0].split('.')[0]*1000000) + int(start_and_end_time[0].split('.')[1])
	end_time =   start_and_end_time[1].split('.')[0]*1000000 + start_and_end_time[1].split('.')[1]
	if absolute_time.microseconds >= start_time and absolute_time <= end_time:
		return True
	return False

def time_greater_than(absolute_time, start_and_end_time):
	end_time =   start_and_end_time[1].split('.')[0]*1000000 + start_and_end_time[1].split('.')[1]
	if absolute_time > end_time:
		return True
	return False

""" Start times will be a file with a list of the start times for each run for an app, so in total 20
	runs. tcp_files will contain 20 files with the format n lines of start_ts, end_ts"""
def create_averages_of_runs(cpu_files, mypath, columns, tcp_files, start_times):
# TODO Get right path for files
	data = create_matrix(4,4)
	count = 0
	num_of_lines = 0
	for i in range(0, len(cpu_files)):
		cpu_files[i] = mypath + '/' + cpu_files[i]
		tcp_files[i] = mypath + '/' + tcp_files[i]

	for z, file in enumerate(cpu_files):
		print cpu_files[z]
		time_counter = 0
		with open(file) as f, open(tcp_files[z]) as t:
			lines  = f.readlines()
			times = t.readLines()
			num_of_lines  = 0
			cpu0 = 0; cpu1 = 0; cpu2 = 0; cpu3 = 0;
			for i in range(1, len(lines)):		# 1 to n as avoiding the first header row
				line = lines[i].split(' ')
				if time_counter >= len(times):
					continue
				start_and_end_time = times[time_counter].split(' ')	
							
				absolute_time = convert_time_stamps_with_starting_time(line[0], start_times[z])
				if len(line) == 9 and time_in_between(absolute_time, start_and_end_time):     
					cpu0 += float(line[columns[0][0]])*float(line[columns[1][0]])/float(2265600)
					cpu1 += float(line[columns[0][1]])*float(line[columns[1][1]])/float(2265600)
					cpu2 += float(line[columns[0][2]])*float(line[columns[1][2]])/float(2265600)
					cpu3 += float(line[columns[0][3]])*float(line[columns[1][3]])/float(2265600)
					num_of_lines += 1
				elif time_greater_than(absolute_time, start_and_end_time):
					time_counter += 1		

			data[0][count/5] += cpu0/float(num_of_lines)			# Divide total by number and add it to data
			data[1][count/5] += cpu1/float(num_of_lines)			# Structured as /5, so every 5 files data shifts to next column
			data[2][count/5] += cpu2/float(num_of_lines)
			data[3][count/5] += cpu3/float(num_of_lines)
		
		count += 1
	
	for i in range(len(data)):								# Divide data by 5 since there a total of 5 runs per app
		for j in range(len(data[i])):
			data[i][j] /= float(5*100)
	return data
	


# Get the files in the directory and sort it by date of creation

apps = ['Firefox', 'Facebook','Messenger', 'Spotify','Dropbox','Youtube']
y_axes = 'Normalized CPU Utilization'
indexes = [ [1, 2, 3, 4],
			[5, 6, 7, 8]
		  ]
for i in range(0, len(apps)):
	mypath = '/Users/nishantr/Downloads/Graphs/gw_gl (kenmore)/'+ apps[i] +'/cpu'
	mtime = lambda f: os.stat(os.path.join(mypath, f)).st_mtime
	files = list(sorted(os.listdir(mypath), key=mtime))
	tcp_files = list(sorted(os.listdir(mypath)))
	#files.sort()
	for i in range(0, len(files), 20):						#Take batch of 20 files to parse for an application
		data = create_averages_of_runs(files[i:i+20], mypath, indexes, [], [])
		generate_plot(data, y_axes, mypath.split('/')[-2]+'_' + y_axes)
		print_matrix(data)
				