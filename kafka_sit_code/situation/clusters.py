import numpy as np

class Cluster:
	def __init__(self,clusterid):
		self.clu_id = clusterid
		self.location = {}
		self.center = None
		self.last_update = None
		self.docs = []
		self.showed_loc = None
		self.type = {}
		self.showed_type = None

	def update_loc(self,location,global_loc):
		if location not in self.location:
			self.location[location] = 0
		self.location[location] += 1
		items = self.location.items()
		items = sorted(items,key= lambda x:x[1],reverse=True)
		if len(items) == 1:
			self.showed_loc = items[0][0]
			return
		if items[0][1] == items[1][1]:
			if global_loc[items[0][0]]> global_loc[items[1][0]]:
				self.showed_loc = items[1][0]
			else:
				self.showed_loc = items[0][0]
		else:
			self.showed_loc = items[0][0]

	def update_type(self,type):
		for t in type:
			if t not in self.type:
				self.type[t] = 0
			self.type[t] += 1
		items = self.type.items()
		items = sorted(items,key= lambda x:x[1],reverse=True)
		self.showed_type = items[0][0]