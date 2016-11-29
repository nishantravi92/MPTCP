import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm


def print_matrix(matrix):
	for i in range(0, len(matrix)):
		for j in range(0, len(matrix[i])):
			print int(matrix[i][j]),
		print ''

def generate_plot(values, y_axis_label, filename, is_util):
	
	interfaces = ['Wifi', 'LTE', 'MPWifi', 'MPLte']
	N = len(values[0]) 
	space = 0.6 #the space between each set of bars
	width = (1 - space+0.2) / (N) #the width of the bars

	x_labels = interfaces[:]
	# for i in range(1,N):
	# 	x_labels.append("Run " + str(i))
	#x_labels.append("Average")


	interface_averages = []
	interfaces_sd = []
	yerr = []
	for i in range(4):
		average = np.average(values[i])
		std = np.std(values[i]) 
		#print average
		#print std 
		#sys.exit()	
		interface_averages.append(average)
		interfaces_sd.append(std)
		#values[i].append(interface_averages[i])
		#yerr.append([0]*(N-1) + [interfaces_sd[i]])
		yerr.append(std)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	pos = [j - (1 - space) / 2. + 0 * width for j in range(1,N+1)]
	wifi = ax.bar(pos, values[0], width, color=cm.Accent(float(0) / N), label = interfaces, yerr = yerr[0])
	pos = [j - (1 - space) / 2. + 1 * width for j in range(1,N+1)]
	lte = ax.bar(pos, values[1], width, color=cm.Accent(float(1) / N), label = interfaces, yerr = yerr[1])
	pos = [j - (1 - space) / 2. + 2 * width for j in range(1,N+1)]
	mpwifi = ax.bar(pos, values[2], width, color=cm.Accent(float(2) / N), label = interfaces, yerr = yerr[2])
	pos = [j - (1 - space) / 2. + 3 * width for j in range(1,N+1)]	
	mplte = ax.bar(pos, values[3], width, color=cm.Accent(float(3) / N), label = interfaces, yerr = yerr[3])


	ax.legend((wifi[0], lte[0], mpwifi[0], mplte[0]), ('Core 0', 'Core 1', 'Core 2', 'Core 3'), bbox_to_anchor=(0., 1.07, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)

	

	ax.set_xticklabels(x_labels)
	ax.set_xticks(range(1, 6))
	ax.set_xlabel("Interfaces")
	if is_util:
		ax.set_ylim([0, 100])
	else:
		ax.set_ylim([0, 2000000])
	ax.set_ylabel(y_axis_label)
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

def create_averages_of_runs(files, mypath, columns):

	data = create_matrix(4,4)
	count = 0
	num_of_lines = 0
	for i in range(0, len(files)):
		files[i] = mypath + '/' +files[i]
	
	for z, file in enumerate(files):
		print files[z]
		with open(file) as f:
			lines  = f.readlines()
			num_of_lines  = 0
			cpu0 = 0; cpu1 = 0; cpu2 = 0; cpu3 = 0;
			for i in range(1, len(lines)):
				#print str(cpu3)+' Line:'+ str(i)
				line = lines[i].split(' ')
				if len(line) != 9:
					continue
				cpu0 += int(line[columns[0]])
				cpu1 += int(line[columns[1]])
				cpu2 += int(line[columns[2]])
				cpu3 += int(line[columns[3]])
				num_of_lines += 1


			data[0][count/5] += cpu0/float(num_of_lines)			# Divide total by number and add it to data
			data[1][count/5] += cpu1/float(num_of_lines)			# Structured as /5, so every 5 files data shifts to next column
			data[2][count/5] += cpu2/float(num_of_lines)
			data[3][count/5] += cpu3/float(num_of_lines)
		
		count += 1
	
	for i in range(len(data)):								# Divide data by 5 since there a total of 5 runs per app
		for j in range(len(data[i])):
			data[i][j] /= float(5)

	return data
	


# Get the files in the directory and sort it by date of creation

apps = ['Facebook','Messenger', 'Firefox', 'Spotify','Dropbox','Youtube']
y_axes = ['CPU Utilization', 'CPU Frequency']
indexes = [ [1, 2, 3, 4],
			[5, 6, 7, 8]
		  ]
for i in range(0, len(apps)):
	mypath = '/Users/nishantr/Downloads/Graphs/bw_gl (kenmore)/'+ apps[i] +'/cpu'
	ctime = lambda f: os.stat(os.path.join(mypath, f)).st_mtime
	files = list(sorted(os.listdir(mypath), key=ctime))
	for j in range(0, len(y_axes)):
		for i in range(0, len(files), 20):						#Take batch of 20 files to parse for an application
			data = create_averages_of_runs(files[i:i+20], mypath, indexes[j])
			flag = False
			if j == 0:
				flag = True
			generate_plot(data, y_axes[j], mypath.split('/')[-2]+'_' + y_axes[j], flag)
				

