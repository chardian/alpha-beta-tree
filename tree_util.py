# 画树用的

from graphviz import Digraph
import sys

dot = Digraph(name='Image', comment='the test', format='png')


class Node(object):
	COUNT = 0

	def __init__(self, parent, value, desc=''):
		self.value = value
		self.desc = desc
		self.parent = parent
		self.children = []
		self.idx = Node.COUNT
		if self.parent is None:
			self.layer = 0
		else:
			self.layer = self.parent.layer + 1
		Node.COUNT += 1

	def update_value(self, value):
		self.value = value

	def add_child(self, value, desc=''):
		temp_node = Node(self, value, desc)
		self.children.append(temp_node)
		return temp_node

	def remove_child(self, child):
		for i in self.children:
			if i == child:
				self.children[i].undo_draw()
				del self.children[i]

	def __str__(self):
		s = ''
		if self.layer == 0:
			pass
		elif self.layer % 2 == 1:
			s = 'AI走'
		else:
			s = '玩家走'

		return s + self.desc + '得分' + str(self.value)

	def draw(self):
		dot.node(label=str(self), name=str(self.idx), fontname="Microsoft YaHei")
		for i in self.children:
			i.draw()
			dot.edge(str(self.idx), str(i.idx), fontname="Microsoft YaHei")
