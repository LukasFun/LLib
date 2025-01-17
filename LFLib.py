# Copyright (c) 2024 Lukas Freudenberg
# 
# Permission is hereby granted, free of charge, to any person 
# obtaining a copy of this software and associated documentation 
# files (the "Software"), to deal in the Software without 
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software 
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be 
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
# OTHER DEALINGS IN THE SOFTWARE.

# 23.04.2024, version 0.3.6
# This module provides a variety of quality of life functions. Some notable examples are:
#	- printing without starting a newline
#	- printing arguments with a single command that can't be joined with "+" like strings
#	- converting a number to a string with nice formatting
#	- a data tip and other useful things for displaying data with matplotlib
#	- a threaded serial port
#
# Changelog
#	- 23.04.2024:	Added functionality to remove an item and all its associated data from a collection of lists,
#					added functionality to recursively remove a tkinter widget and all its children (including from any list they and their data might live in)
#	- 12.04.2024:	Fixed a bug that caused an error when trying to get a file name from an invalid path,
#					added functionality to get a file name for a file without cropping the extension and files without an extension
#	- 09.04.2024:	Added functionality to get a file name from a file path
#	- 08.03.2024:	Added functionality to reorder a list according to a given order
#	- 25.02.2024:	Added functionality to convert a string to a number of seconds
#	- 18.01.2024:	Fixed a bug that caused a crash when trying to automatically open a serial port with no device plugged in
#	- 28.12.2023:	Removed functionality for communication between a process and its subprocesses using files, multiprocessing with communication relying on managed lists is planned
#	- 27.12.2023:	Renamed and continued as LFLib,
#					added functionality to print multiple arguments,
#					added functionality to get the path of the binary executing the parent script,
#					added functionality for communication between a process and its subprocesses using files
#	- 14.10.2022:	Added functionality to automatically connect to a serial port when multiple devices are connected,
#					fixed a bug that caused the module to break under windows
#	- 04.10.2022:	Added functionality to save only the data of individual lines
#	- 30.09.2022:	Added functionality to update the line object of the data tip
#	- 27.06.2022:	Changed serial port functionality to not raise an exception and output a warning instead for writes
#	- 22.06.2022:	Fixed a bug that caused the axis rescaling to not work properly for singular value plots
#	- 21.06.2022:	Added functionality to save the data of a figure as a .csv file,
#					added functionality to get all visible plots (lines) from an axis,
#					added functionality to create a data tip for all plots of an axis,
#					fixed a bug that caused the save path to crash if non integer values were present in the file name
#	- 13.06.2022:	Added functionality to save the data of a plot as a .csv file
#	- 08.06.2022:	Fixed a bug in logarithmic axis scaling,
#					fixed a bug in number formating for Inf and NaN values,
#					fixed a bug that caused the y-axis to not take into account all visible plots
#	- 07.06.2022:	Added functionality to correctly rescale axes where matplotlib fails
#	- 31.05.2022:	Fixed a bug that caused the consecutive file naming to sort the files incorrectly
#	- 30.05.2022:	Changed data tip annotation to automatic string formatting,
#					added functionality to auto format integers
#	- 17.05.2022:	Added functionality to format a number automatically
#	- 16.05.2022:	Added functionality to disable data tip via function
#	- 12.05.2022:	Added option for background color to data tip
#	- 10.05.2022:	Added functionality for data tips
#					added functionality for calculating euclidian distances,
#					added functionality for getting the closest point in an n-dimensional data set to given coordinates using a summation norm
#   - 29.04.2022:	Removed unnecessary elements from vertical toolbar,
#					added functionality to convert a string to a number with respect to German point notation
#   - 26.04.2022:	Added function to enumerate files
#	- 19.04.2022:	Added modular GUI building function,
#					added vertical matplotlib toolbar
#   - 08.04.2022:	Removed debugging code
#   - 05.04.2022:	Added license directly to sourcecode
#   - 31.03.2022:	Removed documentation about custom usage since the library is now available on PyPI,
#					fixed a bug in the buffer clearing of the serial port
#   - 14.02.2022:	Created a workaround for a bug that caused the serial buffer to not clear properly
#					unless updating some specific element in a gui
#   - 26.01.2022:	Fixed a bug that caused writing to a port to fail after a reconnect,
#					lowered reconnect speed in favour of stability
#   - 19.01.2022:	Added functionality to read data from a serial port via a thread
#   - 14.01.2022:	Added functionality to update a canvas with optional refitting of the data,
#					added functionality for reading raw bytes from serial port
#   - 11.01.2022:	Added functionality to update a canvas when an included plot has its data changed
#   - 10.01.2022:	Added functionality for serial ports including automatically re-establishing connection, if disconnected
#   - 07.01.2022:	Initial version
		
import serial
import time
import tkinter as tk
import numpy as np
import threading

import matplotlib.figure as fig
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import glob
import os
from serial.threaded import ReaderThread, Protocol
import serial.tools.list_ports

# Returns the path of the binary executing the parent script
def pyPath():
	return os.environ["_"]

# Custom exception for a closed serial port
class SerialDisconnect(Exception):
	pass

# Prints the argument.
def p(a):
	print(a, end='')

# Prints the argument followed by a newline character.
def pln(*args):
	if len(args) > 0:
		for arg in args:
			p(arg)
	print()

# Converts a number to a string choosing an apopropriate format
# 
# @param a Number to be formatted
# @param point Optional number of decimals after the point (2 by default if applicable)
def fstr(a, point=2):
	# Check type of number
	if isinstance(a, (int, np.integer)):
		return "{0:d}".format(a)
	elif np.isnan(a):
		return "NaN"
	elif np.isinf(a):
		return "Inf"
	elif int(a) == a:
		return fstr(int(a))
	else:
		# Check if the numbers absolute value is too small to be displayed
		if abs(a) < pow(10, -point):
			return "{0:.{1}e}".format(a, point)
		else:
			return "{0:.{1}f}".format(a, point)

# Converts a string into a time in seconds
# 
# @param t string in the format mm:ss or h:mm:ss
# @return number or seconds
def timeToSeconds(t):
	# Check if the input is a string
	if not isinstance(t, str):
		pln("Input ", t, " is not a string.")
		return None
	# Check if the input has the correct format and determine if hours are given
	correctForm = True
	hours = False
	if not t[-3] == ":":
		correctForm = False
	if len(t) >= 6:
		if t[-6] == ":":
			hours = True
		else:
			correctForm = False
	if not correctForm:
		pln("Input ", t, " does not have a proper format.")
		return None
	# Convert input to number of seconds
	seconds = 0
	seconds += int(t[-2:])
	seconds += 60 * int(t[-5:-3])
	if hours:
		seconds += 3600 * int(t[:-6])
	return seconds

# Brings a list into a given new order
# 
# @param a list to be reordered
# @param order list containing the new indices as integers - eg. a=["a", "b", "c"] with order [2, 0, 1] results in ["c", "a", "b"]
def reorder(a, order):
	# check for correct input
	if not (isinstance(a, list) and isinstance(order, list)):
		pln("Input data and order both have to be lists, but they are ", type(a), " and ", type(order), ".")
		return
	l = len(order)
	if not len(a) == l:
		pln("Input data and order both have to be of the same length, but they have length ", len(a), " and ", l, ".")
		return
	# Create new list
	newList = [None]*l
	try:
		for i in range(l):
			newList[i] = a[order[i]]
	except TypeError:
		pln("Order must be a list of integers.")
		return
	except IndexError:
		pln("Order contains an out of bounds index.")
		return
	# Copy content back to original list
	for i in range(l):
		a[i] = newList[i]

# Calculates the length of an array like structure
# 
# Also works with single value inputs
# 
# @param a object to get the length of
# @return length of the oject
def lLen(a):
	pass

# Calculates the euklidian distance between two points
# 
# If one point has fewer coordinates than the other, they will be padded with zeros
# 
# @param point1 Coordinates of the first point
# @param point2 Coordinates of the second point
# @return distance between the points
def distance(point1, point2):
	n = max(len(point1), len(point2))
	point1 = point1 + [0] * (n - len(point1))
	point2 = point2 + [0] * (n - len(point2))
	squareSum = 0
	for i in range(0, n):
		squareSum += pow((point2[i] - point1[i]), 2)
	dist = np.sqrt(squareSum)
	return dist

# Calculates the distance between two points using a summation norm with a customizable unit rhomboid
# 
# If one point has fewer coordinates than the other, they will be padded with zeros
# 
# @param point1 Coordinates of the first point
# @param point2 Coordinates of the second point
# @param unit Dimensions of the unit cuboid
# @return distance between the points
def distanceSum(point1, point2, unit=[1]):
	# Treat all invalid numbers for the unit cuboid as 1
	for i in range(0, len(unit)):
		if unit[i] <= 0:
			unit[i] = 1
	n = max(len(point1), len(point2))
	# Possibly pad inputs
	point1 = point1 + [0] * (n - len(point1))
	point2 = point2 + [0] * (n - len(point2))
	unit = unit + [1] * (n - len(unit))
	# Calculate the distance
	sumDist = 0
	for i in range(0, n):
		sumDist += abs(point2[i] - point1[i]) / unit[i]
	return sumDist

# Finds the closest point in an n-dimensional data set to given coordinates in range using a summation norm
# 
# The area searched for the nearest point is a rhomboid
# 
# @param point
# @param data Data set for coordinates to compare against
# @param dist Array with the maximum distance on the respective axis allowed for the resulting point; ignored if < 0
# @return index of the point closest to the coordinates
def closestPoint(point, data, dist=[-1]):
	# Ensure that the data sets have the same length
	N = len(data[0])
	for i in range(1, len(data)):
		if len(data[i]) != N:
			pln("Data set subarrays must have the same length!")
			return None
	index = None
	curDist = 1
	for i in range(0, N):
		dataPoint = [r[i] for r in data]
		pointDist = distanceSum(point, dataPoint, dist)
		if pointDist <= curDist:
			index = i
			curDist = pointDist
	return index

# Displays the x- and y-value of a point in a plot on a canvas on a mouse click
# 
# Possible todo: Find a solution for plots with logarithmic scaling
class dataTip:
	# Constructor method
	# 
	# @param canvas Canvas to bind data tip to
	# @param ax Axis on the canvas to bind data tip to
	# @param dist Maximum distance from plot data to recognize a click as plot size fraction
	# @param line Plot in the axis to bind data tip to (if none is given, the data tip will work on all plots within the axis instead)
	# @param faceColor Background color of the annotation
	def __init__(self, canvas, ax, dist, line=None, faceColor="w"):
		# Initialize variables
		self.canvas = canvas
		self.ax = ax
		self.line = line
		self.dist = dist
		self.faceColor = faceColor
		self.x1 = 0
		self.y1 = 0
		self.enabled = tk.NORMAL
		
		# Create annotation
		self.annotation = 0
		self.drawAnnotation()
		self.annotation.set_visible(False)
		self.annotated = False
		
		# Bind the click on the canvas
		canvas.mpl_connect('button_press_event', self.handle_clickCanvas)

	# (Re-) Draws the annotation
	def drawAnnotation(self):
		self.annotation = self.ax.annotate("x: " + fstr(self.x1, 2) + "\ny: " + fstr(self.y1, 2), 
			xy=(self.x1, self.y1), xytext=(10, 15),
			textcoords='offset points',
			bbox=dict(alpha=0.5, fc=self.faceColor),
			arrowprops=dict(arrowstyle='->')
		)
		self.annotated = True

	# En- or disables the data tip
	# 
	# @param state Indicates whether to en- or disable the data tip (can be NORMAL or DISABLED)
	def setState(self, state):
		if state == tk.NORMAL:
			self.enabled = state
		elif state == tk.DISABLED:
			self.enabled = state
			self.annotation.remove()
			self.annotated = False
	
	# Updates the line object
	# 
	# @param newLine new line object to be used
	def updateLine(self, newLine):
		self.line = newLine
	
	# Event handler for clicking on the canvas
	def handle_clickCanvas(self, event):
		if self.enabled == tk.NORMAL:
			if self.annotated:
				self.annotation.remove()
				self.annotated = False
			else:
				xL = self.ax.get_xlim()
				yL = self.ax.get_ylim()
				xSpan = xL[1] - xL[0]
				ySpan = yL[1] - yL[0]
				widget = self.canvas.get_tk_widget()
				sizeFac = widget.winfo_height() / widget.winfo_width()
				if self.line != None:
					xData = self.line.get_xdata()
					yData = self.line.get_ydata()
					index = closestPoint([event.xdata, event.ydata], [xData, yData], [self.dist*xSpan, self.dist*ySpan/sizeFac])
					if index != None:
						self.x1, self.y1 = xData[index], yData[index]
						self.drawAnnotation()
				else:
					lines = getVisiblePlots(self.ax)
					xy = []
					for line in lines:
						xData = line.get_xdata()
						yData = line.get_ydata()
						index = closestPoint([event.xdata, event.ydata], [xData, yData], [self.dist*xSpan, self.dist*ySpan/sizeFac])
						if index != None:
							xy += [[xData[index], yData[index]]]
					if len(xy) > 0:
						closest = distanceSum([event.xdata, event.ydata], xy[0], [self.dist*xSpan, self.dist*ySpan/sizeFac])
						self.x1, self.y1 = xy[0]
						for coords in xy:
							pointDist = distanceSum([event.xdata, event.ydata], coords, [self.dist*xSpan, self.dist*ySpan/sizeFac])
							if pointDist < closest:
								closest = pointDist
								self.x1, self.y1 = coords
						self.drawAnnotation()


			updateCanvas(self.canvas, self.ax, False, True)

# Converts a string into a float (if possible) with respect to German point notation
# 
# @param a string to be converted
# @return number (None if input string isn't a number)
def toFloat(a):
	# replace all "," characters with "." to convert German notation to international standard
	a = a.replace(",", ".")
	value = None
	# make sure the input is a number
	try:
		value = float(a)
	except ValueError:
		pass
	return value

# Gets the name of a file from a file path.
# 
# @param path Path of the file.
# @param cropExt Whether to crop the file extention.
# @return The name of the file.
def fileNameFromPath(path, cropExt=True):
	if not isinstance(path, str):
		pln("Path ", path, " must be a string.")
		return None
	cropExtension = 0
	cropDirectory = 0
	if cropExt:
		try:
			# Calculate number of characters for extension
			cropExtension = len(path) - path.rindex(".")
		except ValueError:
			pln("Path: \"", path, "\" doesn't have an extension.")
	try:
		# Calculate number of characters for directory
		cropDirectory = path.rindex("/") + 1
	except ValueError:
		pln("Path: \"", path, "\" has no directory. If the file is in the same directory as the calling program, use: \"./[filename]\".")
	return path[cropDirectory:-cropExtension]

# Calculates the next consecutive number and path to store for a file.
# 
# @param name Base name of the file.
# @param dir Directory to place the file in, relative to the working directory.
# @return Path to save the file in.
def savePath(name, dir):
	# get all previously saved files
	files=glob.glob(dir + name + " *.*")
	# get highest number of a file
	FilesMax = 0
	if len(files) > 0:
		# calculate number of characters before enumeration
		numStart = len(dir + name + " ")
		# calculate number of characters after enumeration
		numCrop = len(files[0]) - files[0].rindex(".")
		for f in files:
			fNum = f[numStart:-numCrop]
			if not fNum.isdigit():
				continue
			if int(fNum) > FilesMax:
				FilesMax = int(fNum)
	# Return string to save file
	return dir + name + " " + str(FilesMax + 1)

# Gets all visible plots of an axis.
# 
# @param ax Axis to get plots from.
# @return List with all visible plots.
def getVisiblePlots(ax):
	# get all lines on the axis
	allLines = ax.lines
	# list to hold only visible lines
	lines = []
	# only consider lines that are visible
	for line in allLines:
		if line.get_visible():
			lines.append(line)
	return lines

# Saves the data of a plot to a .csv file.
# 
# @param plot Plot to be saved.
# @param path Path to save the file to (without file extension).
def savePlotCSV(plot, path):
	f = open(path + ".csv", mode = "w")
	savedataX = plot.get_xdata()
	savedataY = plot.get_ydata()
	if type(savedataX) != list:
		savedataX = savedataX.tolist()
	if type(savedataY) != list:
		savedataY = savedataY.tolist()
	savedataX = str(savedataX)
	savedataY = str(savedataY)
	savedata = savedataX[1:len(savedataX)-1] + "\n" + savedataY[1:len(savedataY)-1]
	f.write(savedata)
	f.close

# Saves the data of a figure to a .csv file.
# 
# The individual axes are separated by two empty lines,
# the plots within each axis are separated by one empty line.
# 
# @param fig Figure to be saved.
# @param path Path to save the file to (without file extension).
def saveFigCSV(fig, path):
	f = open(path + ".csv", mode = "w")
	# get all axes of the figure
	allAx = fig.axes
	for ax in allAx:
		# get all visible lines on the axis
		lines = getVisiblePlots(ax)
		for plot in lines:
			savedataX = plot.get_xdata()
			savedataY = plot.get_ydata()
			if type(savedataX) != list:
				savedataX = savedataX.tolist()
			if type(savedataY) != list:
				savedataY = savedataY.tolist()
			savedataX = str(savedataX)
			savedataY = str(savedataY)
			savedata = savedataX[1:len(savedataX)-1] + "\n" + savedataY[1:len(savedataY)-1] + "\n\n"
			f.write(savedata)
		f.write("\n")
	f.close

# Window to bind events to
window = None

# Rescales an axis with optional keeping of previous limits.
# 
# @param ax The axis to be rescaled.
# @param rescaleX Wheter or not to rescale the x-axis.
# @param rescaleY Wheter or not to rescale the y-axis.
def rescaleAx(ax, rescaleX=True, rescaleY=True):
	if not (rescaleX or rescaleY):
		return
	# list to hold visible lines
	lines = getVisiblePlots(ax)
	if len(lines) == 0:
		return
	if rescaleX:
		xData = lines[0].get_xdata()
		minX = np.min(xData)
		maxX = np.max(xData)
		for line in lines:
			xData = line.get_xdata()
			curMin = np.min(xData)
			curMax = np.max(xData)
			if curMin < minX:
				minX = curMin
			if curMax > maxX:
				maxX = curMax
		# Catch invalid data
		if np.isinf(minX) or np.isnan(minX) or np.isinf(maxX) or np.isnan(maxX):
			return
		if ax.get_xscale() == "linear":
			spaceX = (maxX - minX) / 20
			ax.set_xlim(minX - spaceX, maxX + spaceX)
		else:
			if minX <= 0:
				return
			spaceX = np.log(maxX / minX) / 20
			ax.set_xlim(minX / np.exp(spaceX), maxX * np.exp(spaceX))
	if rescaleY:
		yData = lines[0].get_ydata()
		minY = np.min(yData)
		maxY = np.max(yData)
		for line in lines:
			yData = line.get_ydata()
			curMin = np.min(yData)
			curMax = np.max(yData)
			if curMin < minY:
				minY = curMin
			if curMax > maxY:
				maxY = curMax
		# Catch invalid data
		if np.isinf(minY) or np.isnan(minY) or np.isinf(maxY) or np.isnan(maxY):
			return
		if ax.get_yscale() == "linear":
			spaceY = (maxY - minY) / 20
			ax.set_ylim(minY - spaceY, maxY + spaceY)
		else:
			if minY <= 0:
				return
			spaceY = np.log(maxY / minY) / 20
			ax.set_ylim(minY / np.exp(spaceY), maxY * np.exp(spaceY))

# Updates a canvas with axis in it
def updateCanvas(canvas, ax, rescaleX=True, rescaleY=True):
	# Rescale the axis
	rescaleAx(ax, rescaleX, rescaleY)
	# Update canvas
	canvas.draw()
	# Flush events (if this was called by a tkinter event)
	canvas.flush_events()

# Removes all entries of an item from a list and its associated data from other lists (index based).
# 
# @param item The item to be removed.
# @param lists Lists to remove the item and its associated data from. Must be a tuple of lists, where the first list contains the item itself and subsequent ones its data.
def removeFromLists(item, lists):
	# Check input integrity
	if not isinstance(lists, tuple):
		pln("Lists must be a tuple of lists.")
		return
	if len(lists) == 0:
		pln("No lists given to remove the item from.")
		return
	listLen = len(lists[0])
	for l in lists[1:]:
		if not isinstance(l, list):
			pln("Lists must be a tuple of lists.")
			return
		if not len(l) == listLen:
			pln("Lists are not of the same length.")
			return
	# If there is only one list, no indexing is required
	if len(lists) == 1:
		while lists[0].count(item) > 0:
			lists[0].remove(item)
	else:
		while lists[0].count(item) > 0:
			# Get item index
			index = lists[0].index(item)
			# Remove item
			lists[0].pop(index)
			# Remove all associated data
			for l in lists[1:]:
				l.pop(index)

# Builds a GUI using the tkinter grid manager.
# 
# @param uiElements List of all the widgets to be displayed.
# @param uiGridParams List containing Lists of the parameters required to display the widget as desired.
# Their order is as follows:
# 	0: row
#	1: column
#	2: rowspan
#	3: columnspan
#	4: sticky
def buildUI(uiElements, uiGridParams):
	for k in range(len(uiElements)):
		uiElements[k].grid(row=uiGridParams[k][0], column=uiGridParams[k][1],
								rowspan=uiGridParams[k][2], columnspan=uiGridParams[k][3],
								sticky=uiGridParams[k][4])

# Removes a widget and all its children from the GUI and given lists.
# 
# This doesn't just hide them like pack_forget(), but destroys them. The user can supply a tuple in place of each list to remove list entries by index based on the widget appearing in the first list of the tuple.
# 
# @param widget The widget to be removed.
# @param lists List of Lists that the widget and its children will be removed from. Can also be a list of tuples of lists.
def removeUI(widget, lists):
	# Check input integrity
	if not isinstance(lists, list):
		pln("Argument \"lists\" must be a list of either lists or tuples of lists.")
		return
	if not isinstance(widget, tk.Widget):
		pln("Argument \"widget\" must be a tkinter widget.")
		return
	# Handle the children of the widget first
	children = widget.winfo_children()
	for child in children:
		removeUI(child, lists)
	# Remove widget and associated data from lists
	for l in lists:
		# Check if list is actually a list
		if not isinstance(l, list):
			# Check if list is a tuple with further lists
			if isinstance(l, tuple):
				removeFromLists(widget, l)
			else:
				pln("List to remove from is neither a list nor a tuple of lists.")
				return
		removeFromLists(widget, (l,))
	# Destroy the widget
	widget.destroy()

# Vertical variant of the matplotlib toolbar (lacks the display of the mouse coordinates)
class VerticalPlotToolbar(NavigationToolbar2Tk):
	# Define items used in Toolbar
	toolitems = (
		('Home', 'Reset original view', 'home', 'home'),
		('Pan',
		 'Left button pans, Right button zooms\n'
		 'x/y fixes axis, CTRL fixes aspect',
		 'move', 'pan'),
		('Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),
		('Save', 'Save the figure', 'filesave', 'save_figure'),
	)
	
	def __init__(self, canvas, window):
		super().__init__(canvas, window, pack_toolbar=False)
	
	# override _Button() to re-pack the toolbar button in vertical direction
	def _Button(self, text, image_file, toggle, command):
		b = super()._Button(text, image_file, toggle, command)
		b.pack(side=tk.TOP) # re-pack button in vertical direction
		return b

	# override _Spacer() to create vertical separator
	def _Spacer(self):
		s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
		s.pack(side=tk.TOP, pady=5) # pack in vertical direction
		return s

	# disable showing mouse position in toolbar
	def set_message(self, s):
		pass

# @brief opens a serial port with the given properties.
# @param name Name of the port. If none is given, the connection will be made automatically.
# @param command Optional command to send to the device to initialize it
# @param question Optional command to send to the device to check if the correct connection was made.
# @param answer Expected answer from the device on the given command.
def serPort(name="Auto", command=None, question=None, answer=None, final=None, stopbitsV=None, timeoutV=None, trsctsV=None):
	try:
		if name == "Auto":
			ports=serial.tools.list_ports.comports()
			if len(ports) > 1:
				correctPort = False
				portNum = 1
				while not correctPort and portNum < len(ports):
					prefix = ""
					if os.name == "nt":
						prefix = ""
					elif os.name == "posix":
						prefix = "/dev/"
					name = prefix + ports[portNum].name
					port = serial.Serial(name, timeout=2)
					if command != None:
						port.write(command)
						port.readline()
					if question != None:
						port.write(question)
						ret = port.readline()
						correctPort = ret == answer
					else:
						correctPort = True
					portNum = portNum+1
				if not correctPort:
					raise SerialDisconnect
				if final != None:
					port.write(final)
					port.readline()
			else:
				raise SerialDisconnect
		else:
			port = serial.Serial(name)
		return port
	except (serial.serialutil.SerialException, SerialDisconnect):
		pln("Could not open the serial port! Try un- and replugging the device or providing the correct port name.")
		raise SerialDisconnect

# @brief Protocol for a threaded serial port
# Usage:
#   1. Create object by calling "<port variable> = LLib.sPort(<port name>)"
#   2. Start the thread by calling "<port variable>.start(<maximum buffer size>, <function to call when data is received>)"
# Important notes: 
#   - Currently only supports one serial port open at a time!
#   - Since this port is threaded, it doesn't provide functionality for reading with a timeout!
class sPort(Protocol):
	# Nested class for internal buffer and port
	class Buffer:
		port = None
		content = bytes(0)
		size = 4096
		disconnected = False
		dummyFig = fig.Figure()
		terminator = "\n"

	buffer = Buffer()

	# Placeholder function to be called when data has been read
	def dummy(self):
		pass

	handleData = dummy

	# Constructor method
	def __init__(self, name="Auto", terminatorV="\n"):
		# Create serial port
		self.buffer.port = serPort(name)
		self.buffer.terminator = terminatorV

	# Method start the thread (can't be in the constructor)
	def start(self, maxSize=4096, handleFunc=None):
		# Store function to be called when data is read
		if handleFunc != None:
			sPort.handleData = handleFunc
		# Set the maximum buffer size
		self.buffer.size = maxSize
		# Add a canvas to the dummy figure
		FigureCanvasTkAgg(self.buffer.dummyFig)
		# Initialize reading thread
		self.reader = ReaderThread(self.buffer.port, sPort)
		# Start reading thread
		self.reader.start()

	# Callback function to store read data to the internal buffer and possibly do externally configured tasks
	def readStoreBuffer(self, data):
		# Write data to internal buffer if it fits (discard it otherwise)
		if len(self.buffer.content) + len(data) <= self.buffer.size:
			self.buffer.content += data
		self.handleData()

	# Clear the internal buffer
	def clearBuffer(self, clearLine=False):
		# Flush events
		self.buffer.dummyFig.canvas.flush_events()
		# Update the GUI
		window.update_idletasks()
		if clearLine:
			# Empty the buffer up to the last newline character
			numBytes = len(self.buffer.content)
			for newLineIndex in range(numBytes-1, -1, -1):
				if chr(self.buffer.content[newLineIndex]) == "\n":
					self.buffer.content = self.buffer.content[newLineIndex+1:len(self.buffer.content)]
					break
		else:
			# empty the buffer
			self.buffer.content = bytes(0)

	def connection_made(self, transport):
		"""Called when reader thread is started"""
		pass
		#print("Connected, ready to receive data...")

	def data_received(self, data):
		"""Called with snippets received from the serial port"""
		window.after(0, self.readStoreBuffer, data)

	def reopen(self):
		newPort = None
		try:
			# Get available ports
			ports=serial.tools.list_ports.comports()
			if len(ports) > 1:
				newPort = Serial("/dev/" + ports[1].name)
		except serial.serialutil.SerialException:
			pass
		if newPort != None:
			self.buffer.port = newPort
			self.buffer.disconnected = False
			newReader = ReaderThread(self.buffer.port, sPort)
			newReader.start()
		else:
			window.after(1, self.reopen)

	def connection_lost(self, exc=None):
		pln("Serial port disconnected. Trying to reconnect...")
		self.reopen()
		self.buffer.disconnected = True

	# Returns wether the port is disconnected
	def disconnected(self):
		return self.buffer.disconnected

	# Reads a specified number of bytes (1 if no parameter is given) from the wrapped serial port (if there is data available), 
	# removes it from the buffer and returns it
	def readB(self, bytes=1):
		numBytes = len(self.buffer.content)
		if numBytes < bytes:
			return "not enough data"
		retVal = self.buffer.content[0:bytes]
		self.buffer.content = self.buffer.content[bytes:len(self.buffer.content)]
		return retVal

	# Reads a line from the wrapped serial port (if there is one available), 
	# removes it from the buffer and returns it as a string (without the newline character at the end).
	def readL(self, forceWait=True):
		numBytes = len(self.buffer.content)
		newLineIndex = 0
		for newLineIndex in range(numBytes):
			if chr(self.buffer.content[newLineIndex]) == "\n":
				try:
					retVal = self.buffer.content[0:newLineIndex].decode()
				except UnicodeDecodeError:
					retVal = "Read data isn't a string"
				self.buffer.content = self.buffer.content[newLineIndex+1:len(self.buffer.content)]
				return retVal
		return "not enough data"
	
	# Writes data to the wrapped serial port.
	def write(self, data):
		if self.buffer.disconnected:
			pln("Where are you tryinng to write to? The port is closed!")
			return
		try:
			self.buffer.port.write(data)
		except OSError:
			pln("Error in writing (the port is probably closed but hasn't noticed yet)")
	
	# Writes a line to the wrapped serial port.
	def writeL(self, s):
		if self.buffer.disconnected:
			pln("Where are you tryinng to write to? The port is closed!")
			return
		try:
			self.buffer.port.write((s + '\n').encode())
		except OSError:
			pln("Error in writing (the port is probably closed but hasn't noticed yet)")
