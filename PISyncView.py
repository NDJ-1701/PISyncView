
import tkinter as tk

# class Flow(list):
# 	def __init__(self):
# 		self.fullString = ""

class Line():
	def __init__(self, string, step, time):
		self.str = string
		self.time = time
		self.step = step

def flow_filter(logFile, flowNum):
	with open(logFile, 'r') as f:
		output = ""
		step = ""
		active = False
		for line in f:
			step += line
			if line.startswith("========"):
				if active:
					output += step
				step = ""
			elif line.startswith("FLOW {} is active".format(flowNum)):
				active = True
			elif line.startswith("FLOW {} is blocked".format(flowNum)):
				active = False
		if active:
			output += step + "\n========================\n"
	return "========================\n" + output

def addLineToAllActiveFlows(line, activeFlows, flows, tag):
	#modify this later so we can add any number of tags.
	for flowIndex in activeflows:
		flow = flows[flowIndex]
		flow.insert("end", line, tag)


def parseLogFile(dumpFilePath, flows):
	with open(dumpFilePath, 'r') as f:
		numFlows = len(flows)
		
		# initialize loop vars. Most must also be reset each time the buffer is committed to the flow text.
		activeflows = [] # [1, 2, 3, etc]
		activeOp = [] # will be an array where index is flow - 1 and value is current op #
		for i in range(numFlows): # initialize so we can write to any of the valid indexes
			activeOp.append(0)
		time = -1.0
		step = -1
		flowSpecific = 0 # 0 for no flow is specific, an integer if within flow specific code.
		opStart = True # to keep track of whether we are in the buffering section
		allFlowsBuffer = []
		flowSpecificBuffer = []
		# start the parsing
		for line in f:
			if opStart:
				if not flowSpecific:
					allFlowsBuffer.append(line)

				if flowSpecific and (line.startswith("Tool Group") or (line.startswith("FLOW ") and "active" in line)): # end of an active flow's op start
					# write buffer to last registered flow along with tags based on line contents
					# To Do: instead of the below generic line add, add tagged lines
					for bLine in allFlowsBuffer:
						flows[flowSpecific - 1].insert("end", bLine)
					for bLine in flowSpecificBuffer:
						flows[flowSpecific - 1].insert("end", bLine)
					flowSpecificBuffer = []

				if line.startswith("FLOW ") and "active" in line:
					flowSpecific = int(line[ line.index("FLOW ")+5: line.index(" is") ])
					activeflows.append(flowSpecific)
				if flowSpecific:
					flowSpecificBuffer.append(line)
					if line.startswith("New op: "):
						newOpNumber = int(line[ line.index("New op: ")+8: line.index(100) ]) # 100 is arbitrary, I assume this will grab until end of line
						activeOp[flowSpecific - 1] = newOpNumber
				if line.startswith("Tool Group"):
					opStart = False
					allFlowsBuffer = []
					# To Do: add this line to all flows
			else: # not opStart
				# At the end of each step, put those lines into the active flows
				if line.startswith("+-+-"):
					for flowIndex in activeflows:
						flow = flows[flowIndex]
						for bLine in buffer[flowIndex]:
							#put buffer into each active flow along with step # and time.
							flows[flow-1].append(Line(bLine, step, time))
							flow.insert("end", bLine, step, time)
					#clear step specific vars
					activeflows = []
					buffer = []
					time = -1.0
					step = -1
					opStart = True
					allFlowsBuffer = []
				elif line.startswith("Time"):
					# line has time store time
					time = float(line[line.index("= ")+2:line.index(" min")])
				elif line.startswith("STEP "):
					# line has step, store step number
					step = int(line[line.index("STEP ")+5:line.index(" (")])


# Custom Scroll functions
def all_yview(*args):
	""" Called by the scrollbar to set the 
	position of	the text views.
	"""
	print("yview args", args)
	T1.yview(*args)
	T2.yview(*args)

def all_scroll_set(*args):
	""" Called by the text views to set the 
	position of the scrollbar.
	"""
	print("scroll_set args", args)
	S.set(*args)

# general configuration of the tkinter text widgets
def configure_text(text):
	text.tag_configure("header", background="black", foreground="white", spacing1=10, spacing3=10)
	text.config(width=70)

if __name__ == '__main__':
	

	# get file path, currently static
	dumpFilePath = "Test_Part_2_6099.txt";
	
	# get number of flows
	numflows = 1
	with open(dumpFilePath, 'r') as f:
		numFlows = f.readline().count(',') + 1
	
	# initialize Tkinter root window/containter
	rootTk = tk.Tk(className="Step/Flow Viewer")

	# Create text containers
	flows = []
	for i in range(numFlows):
		tkText = tk.Text(rootTk)
		configure_text(tkText)
		tkText.pack(side='left', fill='y')
		flows.append(tkText)

	# process dump, parsing info, assigning to flow, applying tags.
	parseLogFile(dumpFilePath, flows)

	for i, flow in enumerate(flows):
		w = windows[i]
		#w.config(yscrollcommand=S.set)
		#w.config(width=70)
		for line in flow:
			w.insert("end", line.str, line.step)

	#S.config(command=all_yview)

	# Configure window
	rootTk.config(height=30)
	rootTk.resizable(False, True)

	# Display the window and keep listening for events
	rootTk.mainloop()
    