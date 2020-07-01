from graphics import *
from tree_util import *

CELL = 100  # 边长
SCREEN_SIZE = 500

PLAYER = 1
AI = 2
DEPTH = 3  # 搜索深度
ENABLE_TREE_IMAGE = True  # 开启后，AI每步都会生成alpha-beta树图片，并自动打开


def get_pos_desc(x, y):
	desc = ''
	if x == 0:
		desc = '左'
	elif x == 1:
		desc = '中'
	elif x == 2:
		desc = '右'
	if y == 0:
		if x == 1:
			return '上'
		else:
			return desc + '上角'
	if y == 2:
		if x == 1:
			return '下'
		else:
			return desc + '下角'
	return desc


def simple_num(n):
	"""
	简化显示正负无穷，让生成的图片稍微小一点
	"""
	if n == sys.maxsize:
		return '正无穷'
	elif n == -sys.maxsize:
		return '负无穷'
	else:
		return str(n)


class PlayerAction(object):
	def __init__(self, x, y, belong):
		self.x = x
		self.y = y
		self.belong = belong

	def __str__(self):
		# 记录下棋的步骤，用于debug中查看
		s = get_pos_desc(self.x, self.y)
		if self.belong == AI:
			return '电脑：' + s
		else:
			return '玩家：' + s


class Board(object):
	def __init__(self):
		super(Board, self).__init__()
		self.win = None
		self.offset_x = 90
		self.offset_y = 90
		self.history = []  # 下过的棋
		self.board = []

	def reset_board(self):
		self.board = [0 for i in range(0, 9)]  # 棋盘。0未下 1:Player 2:AI
		if self.win is not None:
			self.win.close()
		self.draw_board()

	def move(self, x, y, belong):
		self.board[x * 3 + y] = belong
		self.history.append(PlayerAction(x, y, belong))

	def undo_move(self, x, y):
		self.board[x * 3 + y] = 0
		self.history.pop()

	def draw_piece(self, x, y, belong, turn):
		qi = Circle(self.get_piece_pos(x, y), 40)
		if belong == PLAYER:
			qi.setFill('black')
		else:
			qi.setFill('white')
		qi.draw(self.win)
		msg = Text(self.get_piece_pos(x, y), str(turn))
		msg.setFill('grey')
		msg.setSize(20)
		msg.draw(self.win)

	def all_line(self):
		return [
			self.board[0:3], self.board[3:6], self.board[6:9],
			self.board[0::3], self.board[1::3], self.board[2::3],
			self.board[0::4], self.board[2:7:2]
		]

	def is_full(self):
		for i in self.board:
			if i == 0:
				return False
		return True

	def get_available_pos(self):
		for idx, value in enumerate(self.board):
			if value == 0:
				yield idx // 3, idx % 3

	def get_offset_pos(self, x, y):
		return Point(x + self.offset_x, y + self.offset_y)

	def get_piece_pos(self, x, y):
		return Point(self.offset_x + (x + 0.5) * CELL, self.offset_y + (0.5 + y) * CELL)

	def draw_board(self):
		self.win = GraphWin('game', SCREEN_SIZE, SCREEN_SIZE)
		self.win.setBackground('grey')
		# 绘制棋盘
		i = 0
		size = CELL * 3
		while i <= size:
			l = Line(self.get_offset_pos(i, 0), self.get_offset_pos(i, size))
			l.draw(self.win)
			i += CELL
		i = 0
		while i <= size:
			l = Line(self.get_offset_pos(0, i), self.get_offset_pos(size, i))
			l.draw(self.win)
			i += CELL

	def capture_player_input(self):
		pos = self.win.getMouse()
		x = (pos.getX() - self.offset_x) // CELL
		y = (pos.getY() - self.offset_y) // CELL
		return int(x), int(y)

	def is_available_pos(self, x, y):
		return self.board[x * 3 + y] == 0

	def show_message(self, content):
		message = Text(Point(250, 250), content)
		message.setFill('green')
		message.setSize(35)
		message.draw(self.win)

	def pause(self):
		self.win.getMouse()


class Game(object):
	def __init__(self):
		super(Game, self).__init__()
		self.board = Board()
		self.board.reset_board()
		self.next_ai_point = (0, 0)
		self.turn = 0
		self.root_node = None
		# self.test()
		self.start_game()

	def test(self):
		"""快速测试指定棋局"""
		self.play_a_piece(1, 0, PLAYER)
		self.play_a_piece(1, 1, AI)
		self.play_a_piece(0, 1, PLAYER)
		self.play_a_piece(0, 0, AI)
		self.play_a_piece(2, 2, PLAYER)

	def start_game(self):
		game_over = False
		while not game_over:
			if self.turn % 2 == 0:
				x, y = self.board.capture_player_input()
				if x < 0 or y < 0 or x > 2 or y > 2:
					print("点到了屏幕之外")
					continue
				if not self.board.is_available_pos(x, y):
					print('这个点不能再下了')
					continue
				belong = PLAYER
			else:
				belong = AI
				x, y = self.ai()
			self.play_a_piece(x, y, belong)
			if self.check_game_over():
				self.turn = 0
				self.board.pause()
				self.board.reset_board()
				continue

	def play_a_piece(self, x, y, belong):
		self.board.draw_piece(x, y, belong, self.turn)
		self.board.move(x, y, belong)
		self.turn += 1

	def check_game_over(self):
		s = ''
		if self.game_win(AI):
			s = '电脑赢了'
		elif self.game_win(PLAYER):
			s = '你赢了'
		elif self.board.is_full():
			s = '平局'

		if s != '':
			self.board.show_message(s)
			return True
		return False

	def game_win(self, belong):
		for line in self.board.all_line():
			if line[0] == line[1] and line[1] == line[2] and line[0] == belong:
				return True
		return False

	def ai(self):
		dot.clear()
		self.root_node = Node(None, 0)
		value = self.neg_max(True, DEPTH, -sys.maxsize, sys.maxsize, self.root_node)
		if ENABLE_TREE_IMAGE:
			self.root_node.update_value(value)
			self.root_node.draw()
			dot.view(filename='haha', directory='.')
		return self.next_ai_point

	def neg_max(self, is_ai, depth, alpha, beta, node):
		"""
		:param is_ai: 是否是AI
		:param depth: 深度
		:param alpha: 取值范围：对方下完棋之后，当前玩家保证能拿的最低分
		:param beta: 取值范围：对方下完棋之后，当前玩家能拿最高的分，如果计算出出现比beta更高的值，对方肯定不让这种事情发生，不要幻想敌人给机会。
		:param node: 画图用的节点
		:return: 返回最优解的值
		"""
		if self.game_win(PLAYER) or self.game_win(AI) or depth == 1 or self.board.is_full():
			vv = self.get_score(is_ai)
			# print('depth,alpha, 判断结束了', depth, vv)
			return vv
		blank_list = self.board.get_available_pos()
		for x, y in blank_list:
			belong = AI if is_ai else PLAYER
			self.board.move(x, y, belong)
			child_node = node.add_child(0, get_pos_desc(x, y) + ',' + simple_num(alpha) + ',' + simple_num(beta))
			value = -self.neg_max(not is_ai, depth - 1, -beta, -alpha, child_node)
			child_node.update_value(value)
			# print('\t' * (DEPTH - depth) + str(value))
			# print('{}{}:{}'.format('\t' * (DEPTH - depth), get_pos_desc(x, y), value))
			self.board.undo_move(x, y)
			# 测试打印
			if depth == DEPTH:
				print('AI尝试走' + get_pos_desc(x, y), '分数是' + str(value))
			if value > alpha:
				if depth == DEPTH:
					# print('得到了结果吧', x, y)
					self.next_ai_point = (x, y)
				if value >= beta:
					# print('剪枝了？')
					return beta
				alpha = value
		# print('depth,alpha', depth, alpha)
		return alpha

	def get_score(self, is_ai):
		"""
		遍历8条线，获取当前执棋对象的棋势得分
		"""
		score = 0
		for line in self.board.all_line():
			score = score + self.get_score_line(is_ai, line)
			score = score - self.get_score_line(not is_ai, line)
		return score

	def get_score_line(self, is_ai, arr):
		"""
		获取一条线上的得分
		"""
		n = 0
		if is_ai:
			if AI in arr and PLAYER not in arr:
				n = sum(arr) / AI
		else:
			if AI not in arr and PLAYER in arr:
				n = sum(arr) / PLAYER
		if n == 1:
			return 10
		if n == 2:
			return 100
		if n == 3:
			return 10000
		if n == 0:
			if arr[0] == arr[1] and arr[1] == arr[2] and arr[2] == 0:
				return 5
		return 0


if __name__ == '__main__':
	g = Game()
	g.start_game()
