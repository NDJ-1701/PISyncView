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

def addLineToAllActiveFlows(line, activeFlows, flows, tag="normal"):
	#modify this later so we can add any number of tags.
	for flow in activeFlows:
		flow = flows[flow - 1] # subtract 1 to get index, flow 1 = index 0
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
				if flowSpecific:
					if (line.startswith("Tool Group") or (line.startswith("FLOW ") and "active" in line)): # end of an active flow's op start
						# write buffer to last registered flow along with tags based on line contents
						# To Do: instead of the below generic line add, add tagged lines
						for bLine in allFlowsBuffer:
							if bLine.startswith("STEP"):
								flows[flowSpecific - 1].insert("end", bLine, "newStep")
							else:
								flows[flowSpecific - 1].insert("end", bLine)
						for bLine in flowSpecificBuffer:
							if not bLine.startswith("FLOW "):
								flows[flowSpecific - 1].insert("end", bLine, "flowSpecific")
						flowSpecificBuffer = []
						if line.startswith("FLOW ") and "active" in line:
							flowSpecific = int(line[ line.index("FLOW ")+5: line.index(" is") ])
							activeflows.append(flowSpecific)
							flowSpecificBuffer.append(line)
						elif line.startswith("Tool Group"):
							flowSpecific = 0
							opStart = False
							allFlowsBuffer = []
							addLineToAllActiveFlows(line, activeflows, flows, "header")
							continue
					else:
						flowSpecificBuffer.append(line)
						if line.startswith("New op: "):
							newOpNumber = int(line[ line.index("New op: ")+8: 100 ]) # 100 is arbitrary, I assume this will grab until end of line
							activeOp[flowSpecific - 1] = newOpNumber
				else: # not flowSpecific:
					if line.startswith("FLOW ") and "active" in line:
						flowSpecific = int(line[ line.index("FLOW ")+5: line.index(" is") ])
						activeflows.append(flowSpecific)
						flowSpecificBuffer.append(line)
					else:
						allFlowsBuffer.append(line)
						if line.startswith("Time"):
							# line has time store time
							time = float(line[line.index("= ")+2:line.index(" min")])
						elif line.startswith("STEP "):
							# line has step, store step number
							step = int(line[line.index("STEP ")+5:line.index(" (")])
			else: # not opStart
				# process all headers, else add line without header.
				if line.startswith("Workpiece Information") or line.startswith("Axis Information") or line.startswith("Errors"):
					addLineToAllActiveFlows(line, activeflows, flows, "header")
				else:
					addLineToAllActiveFlows(line, activeflows, flows, "hidden")
				if line.startswith("+-+-"):
					# a new op is about to start.
					opStart = True
					#clear step specific vars
					activeflows = []
					buffer = []
					time = -1.0
					step = -1
					allFlowsBuffer = []

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

def toggle_visibility(event):
	text = event.widget
	block_start, block_end = get_block(text, "insert")
	# is any of the text tagged with "hidden"? If so, show it
	next_hidden = text.tag_nextrange("hidden", block_start, block_end)
	if next_hidden:
		text.tag_remove("hidden", block_start, block_end)
	else:
		text.tag_add("hidden", block_start, block_end)


def get_block(text, index):
	'''return indicies after header, to next header, next step, or EOF'''
	start = text.index("%s lineend+1c" % index)
	next_header = text.tag_nextrange("header", start)
	next_step = text.tag_nextrange("newStep", start)
	if next_step < next_header:
		next_header = next_step
	if next_header:
		end = next_header[0]
	else:
		end = self.text.index("end-1c")
	return (start, end)


# general configuration of the tkinter text widgets
def configure_text(text):
	text.tag_configure("header", background="dark gray", foreground="black", font='Helvetica 10 bold', spacing1=2, spacing3=3)
	text.tag_bind("header", "<Double-1>", toggle_visibility)
	text.tag_configure("newStep", background="dark red", foreground="light gray", font='Helvetica 10 bold', spacing1=6, spacing3=6)
	text.tag_configure("flowSpecific", foreground="light green")
	text.tag_configure("hidden", elide=True)
	text.config(width=70)
	text.config(background="black", foreground="light gray")
	text.pack(side='left', fill='y')

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
		configure_text(tkText) # all styling and configuration done here.
		flows.append(tkText)

	# process dump, parsing info, assigning to flow, applying tags.
	parseLogFile(dumpFilePath, flows)

	#S.config(command=all_yview)

	# Configure window
	rootTk.config(height=30)
	rootTk.resizable(False, True)

	# Display the window and keep listening for events
	rootTk.mainloop()