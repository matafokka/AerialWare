"""
AerialWare 
Copyright (C) 2019 matafokka

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QGraphicsPixmapItem, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem, QGraphicsPolygonItem
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtGui import QPixmap, QPolygonF, QBrush, QPen, QColor, QTransform, QPainter
from PyQt5.QtCore import QPointF, QLineF, Qt
# For loading ui file
from PyQt5.uic import loadUi
from sys import argv, exit

# Main window of application
class Window(QMainWindow):
	def __init__(self):
		# Make this app super awesome
		super().__init__()
		# Load UI from file
		loadUi('ui/mainwindow.ui', self)
		# Initialize step 1
		self.stepOne()

	##################
	def stepOne(self):
		"""Step 1 -- loading image, connecting events to controls
		"""
		self.disableItems()
		self.comboLang.setVisible(False) # Hide language panel because there are no additional languages yet
		# Connect events
		self.btnOpenImage.clicked.connect(self.loadImage)
		self.btnNext.clicked.connect(self.stepTwo)
		self.btnIncreaseZoom.clicked.connect(self.increaseZoom)
		self.btnDecreaseZoom.clicked.connect(self.decreaseZoom)
		self.editZoom.textEdited.connect(self.setZoom)

	def loadImage(self):
		# Open file dialog and get path
		file = QFileDialog.getOpenFileName(self, 'Open image', '', 'Images (*.jpg *.jpeg *.png *.bmp);;All files (*)')[0]

		# Create a pixmap from file
		img = QPixmap(file)

		# Check if it's an image
		if not img.isNull():
			# Set opened image to the scene
			item = QGraphicsPixmapItem(img)
			self.scene = QCustomScene()
			self.scene.addItem(item)
			self.Image.setScene(self.scene)
			self.height = img.height()
			self.width = img.width()
			self.enableItems()

		elif file != "":
			# If it's not image and user didn't press 'Cancel' raise an error message
			self.disableItems()
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setWindowTitle("AerialWare - Invalid image")
			msg.setText("It's not an image. Please open a valid image.")
			msg.exec_()

	def enableItems(self):
		"""Enables controls
		"""
		self.editZoom.setEnabled(True)
		self.btnDecreaseZoom.setEnabled(True)
		self.btnIncreaseZoom.setEnabled(True)
		self.btnNext.setEnabled(True)

	def disableItems(self):
		"""Disables controls
		"""
		self.editZoom.setEnabled(False)
		self.btnDecreaseZoom.setEnabled(False)
		self.btnIncreaseZoom.setEnabled(False)
		self.btnNext.setEnabled(False)
	##################

	def stepTwo(self):
		"""Step 2 -- Needed only for first click. Step 3 does all the job.
		"""
		self.turnPage()
		self.btnNext.disconnect()
		self.btnNext.clicked.connect(self.stepThree)

	##################

	def stepThree(self):
		"""Step 3 -- Do basically everything.
		"""

		# Validate data
		def setError(s):
			"""Formats string for displaying
			"""
			self.lblDataError.setText("<html><head/><body><div style='font-size: 12pt'>Can't procede, " + s + "</div></body></html>")

		# Try to read data
		try:
			xTL = float(self.xTopLeft.text())
			xTR = float(self.xTopRight.text())
			xBL = float(self.xBottomLeft.text())
			xBR = float(self.xBottomRight.text())

			yTL = float(self.yTopLeft.text())
			yTR = float(self.yTopRight.text())
			yBL = float(self.yBottomLeft.text())
			yBR = float(self.yBottomRight.text())

			xD = float(self.xDelimiter.text())
			yD = float(self.yDelimiter.text())
		except:
			# Write error message
			setError("some fields contains non-numeric values. Please recheck everything and click \"Next\" again.")
			return

		# Check for metric errors
		errors = ""
		if xD <= 0:
			errors += "longtitude"
		if yD <= 0:
			if errors != "":
				errors += " and "
			errors += "latitude"

		if errors != "":
			setError("delimiters should be more than zero. Please set correct " + errors + " delimiter.")
			return

		# And calculate px / deg ratio, i.e. deg * (px / deg) = px
		try:
			self.xDTop = int(self.width / abs(xTL - xTR) * xD)
			self.xDBottom = int(self.width / abs(xBL - xBR) * xD)
			self.yDLeft = int(self.height / abs(yTL - yBL) * yD)
			self.yDRight = int(self.height / abs(yTR - yBR) * yD)
		except ZeroDivisionError:
			setError("some given corners are at the same point. Please recheck every coordinate.")
			return

		errors = ""
		if self.xDTop > self.width:
			errors += "Longtitude delimiter is less than given size of top of the image. Please check longtitude of top corners.<br>"
		if self.xDBottom > self.width:
			errors += "Longtitude delimiter is less thagiven n size of bottom of the image. Please check longtitude of bottom corners.<br>"
		if self.yDLeft > self.height:
			errors += "Latitude delimiter is less than given size of left of the image. Please check latitude of left corners.<br>"
		if self.yDRight > self.height:
			errors += "Latitude delimiter is less than diven size of right of the image. Please check latitude of right corners.<br>"

		if errors != "":
			setError("something's wrong with given data:<br>" + errors)
			return

		self.turnPage()

		# Draw grid
		def intersection(x1, y1, x2, y2, x3, y3, x4, y4):
			"""Calculates intersection on two lines
			Args:
				x1, y1 -- first point of first line
				x2, y2 -- second point of first line
				x3, y3 -- first point of second line
				x4, y4 -- second point of second line
				These coordintaes must represent coordinates in pixels
			Returns:
				QPointF(x, y) -- intersection of two given lines
			"""
			divider = ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
			if divider == 0:
				return None
			x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / divider
			y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / divider
			return QPointF(int(x), int(y))

		# Set points for grid
		# Points will look like:
		# [point, point, ...],
		# [point, point, ...], ...
		point_rows = []
		# Let x1, y1; x2, y2 be vertical line
		# and x3, y3; x4, y4 be horizontal line.
		# Thus, y1 and y2 should be always on top and bottom;
		# x3, x4 -- on left and right
		y1, y2, x3, x4 = 0, self.height, 0, self.width
		# So we have to change:
		#	for vertical line: x1, x2
		#	for horizontal line: y3, y4
		
		y3 = y4 = 0 # Initial values for horizontal line
		# Move horizontal line
		while y3 <= self.height or y4 <= self.height:
			x1 = x2 = 0 # Initial values for vertical line
			# Move vertical line
			points = []
			while x1 <= self.width or x2 <= self.width:
				point = intersection(x1, y1, x2, y2, x3, y3, x4, y4)
				if point != None:
					points.append(point)
				x1 += self.xDTop
				x2 += self.xDBottom
			if points != []:
				point_rows.append(points)
			y3 += self.yDLeft
			y4 += self.yDRight
		
		# If nothing has been added
		if points == []:
			setError("can't generate grid. I dont even know how you managed to get this error. Please recheck coordinates and try again.")
			return

		# Get scene geometry to preserve scene expanding
		rect = self.scene.sceneRect()
		# And add bounds for the grid
		self.bounds = QGraphicsRectItem(rect)
		self.bounds.setFlag(self.bounds.ItemClipsChildrenToShape)
		self.scene.addItem(self.bounds)
		# Create polygons from points
		# We'll recheck previous item
		i = 1 # Rows
		while i < len(point_rows):
			j = 1 # Points
			while j < len(point_rows[i]):
				# Add points in following order: top left, top right, bottom right, bottom left
				points = [
					point_rows[i - 1][j - 1],
					point_rows[i - 1][j],
					point_rows[i][j],
					point_rows[i][j - 1]
				]
				# We're assigning self.bounds as parent implicitly, so we shouldn't add polygon to scene by ourselves.
				poly = QCustomGraphicsPolygonItem(QPolygonF(points), self.bounds)
				poly.setRowCol(i - 1, j - 1)
				j += 1
			i += 1
		# Restore scene geometry
		self.scene.setSceneRect(rect)
		
		self.turnPage()
		self.btnDraw.clicked.connect(self.scene.drawPaths)
		self.btnNext.setText("Save")
		self.btnNext.disconnect()
		self.btnNext.clicked.connect(self.save)

	##################

	def save(self):
		"""Saves user results
		"""
		rect = self.scene.sceneRect()
		file = QFileDialog.getSaveFileName(self, 'Save file', '', 'Vector Image (*.svg)')[0]
		if file == "":
			return
		gen = QSvgGenerator()
		gen.setFileName(file)
		gen.setSize(rect.size().toSize())
		gen.setViewBox(rect)
		painter = QPainter(gen)
		self.scene.render(painter)
		painter.end()
		exit(None)

	##################
	
	# Misc stuff
	def changeLanguage(self):
		"""Changes language. Not implemented yet.
		"""
		pass
		
	def turnPage(self):
		"""Turns page of "Steps"
		"""
		self.Steps.setCurrentIndex(self.Steps.currentIndex() + 1)

	def increaseZoom(self):
		"""Zooms image in
		"""
		value = float(self.editZoom.text()) + 10
		self.editZoom.setText(str(value))
		self.setZoom()

	def decreaseZoom(self):
		"""Zooms image out
		"""
		value = float(self.editZoom.text()) - 10
		if value >= 10:
			self.editZoom.setText(str(value))
			self.setZoom()

	def setZoom(self):
		"""Sets zoom
		"""
		try:
			value = float(self.editZoom.text()) * 0.01
		except ValueError:
			self.editZoom.setText("100.0")
			self.setZoom()
			return
		self.Image.resetTransform()
		self.Image.scale(value, value)
		
##################

# Custom subclasses

class QCustomScene(QGraphicsScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs) 
		self.customSelectedItems = []

	def mousePressEvent(self, event):
		"""Checks and unchecks squares under cursor if RMB has been pressed
		"""
		if event.button() != Qt.RightButton:
			return
		item = self.itemAt(event.scenePos(), QTransform())
		if not isinstance(item, QCustomGraphicsPolygonItem):
			return

		if item in self.customSelectedItems:
			index = self.customSelectedItems.index(item)
			self.customSelectedItems.pop(index)
			item.setBrush(item.uncheckBrush)
		else:
			self.customSelectedItems.append(item)
			item.setBrush(item.checkBrush)

	def selectedItems(self):
		return self.customSelectedItems

	def drawPaths(self):
		"""Draws both flight path
		"""
		# Remove existing lines
		for item in self.items():
			if isinstance(item, QGraphicsLineItem):
				self.removeItem(item)
		# Draw paths
		items = self.selectedItems()
		self.drawPath(items, True)
		self.drawPath(items, False)
		self.update()
	
	def drawPath(self, items, use_rows):
		"""Draws one flight path
		Args
		items -- squares.
		use_rows:
			True -- go by rows
			False -- go by cols
		"""
		if use_rows:
			way = "row"
			sort_second = "col"
			old_side = "left"
			new_side = "right"
			color = QColor(255, 10, 10)
		else:
			way = "col"
			sort_second = "row"
			old_side = "top"
			new_side = "bottom"
			color = QColor(10, 255, 10)
		
		# Pen for main lines
		pen = QPen(color)
		pen.setWidth(2)
		# Pen for turning lines
		pen2 = QPen(color)
		pen2.setWidth(2)
		pen2.setStyle(Qt.DashLine)
		pen2.setDashOffset(2)

		# Sort selected items
		items.sort(key=lambda item: item.getRowCol()[sort_second])
		items.sort(key=lambda item: item.getRowCol()[way])

		# Draw lines
		new_pos = True # Shows if we're will be at new col/row at next iteration
		prev_line = None # Previously drawn line
		is_last_point_reversed = False # Shows from which end draw turning line
		for i in range(len(items)):
			item = items[i]
			if new_pos:
				side1 = item.getSides()[old_side]
				new_pos = False
			pos = item.getRowCol()[way]
			try:
				next_pos = items[i + 1].getRowCol()[way]
			except:
				next_pos = pos + 1
			if pos != next_pos:
				side2 = item.getSides()[new_side]
				lineF = QLineF(side1, side2)
				line = QGraphicsLineItem(lineF)
				line.setPen(pen)
				self.addItem(line)
				new_pos = True
				if prev_line != None:
					if is_last_point_reversed:
						start = prev_line.p2()
						end = side2
					else:
						start = prev_line.p1()
						end = side1
					new_line = QGraphicsLineItem(QLineF(start, end))
					new_line.setPen(pen2)
					self.addItem(new_line)
				is_last_point_reversed = not is_last_point_reversed
				prev_line = lineF


class QCustomGraphicsPolygonItem(QGraphicsPolygonItem):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Set appearance
		pen = QPen(QColor(30, 30, 255))
		pen.setWidth(2)
		self.setPen(pen)
		self.checkBrush = QBrush(QColor(130, 130, 255, 100))
		self.uncheckBrush = QBrush(QColor(0, 0, 0, 0))

		# Calculate centers of polygon's sides
		def getSide(p1, p2):
			x1, x2, y1, y2 = p1.x(), p2.x(), p1.y(), p2.y()
			return QPointF(
				min(x1, x2) + abs((x1 - x2) / 2),
				min(y1, y2) + abs((y1 - y2) / 2)
			)
		points = self.polygon()
		# Check Step 3 to understand magic numbers below
		self.left = getSide(points[0], points[3])
		self.right = getSide(points[1], points[2])
		self.top = getSide(points[0], points[1])
		self.bottom = getSide(points[3], points[2])
	
	def getSides(self):
		"""Returns dictionary of sides
		"""
		return {
			"left": self.left,
			"right": self.right,
			"top": self.top,
			"bottom": self.bottom
		}
	
	def setRowCol(self, row, col):
		"""Sets row and column of square in a grid
		"""
		self.row = row
		self.col = col

	def getRowCol(self):
		"""Returns dict with row and column
		"""
		return {
			"row": self.row,
			"col": self.col
		}

if __name__ == '__main__':
	# Create an instance of QApplication
	app = QApplication(argv)
	# Create an instance of our Window class
	window = Window()
	# Show window
	window.show()
	# Execute app and also write action for exiting
	exit(app.exec_())
