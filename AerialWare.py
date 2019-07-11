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

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QGraphicsPixmapItem, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem, QGraphicsPolygonItem, QWidget, QVBoxLayout
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtGui import QPixmap, QPolygonF, QBrush, QPen, QColor, QTransform, QPainter
from PyQt5.QtCore import QPointF, QLineF, Qt, pyqtSignal
from PyQt5.uic import loadUi  # For loading ui files
from sys import argv, exit
import importlib
import os

# Main window of application
class Window(QMainWindow):
	"""Places AerialWare into QMainWindow. Uses predefined .ui file.
	"""
	def __init__(self):
		super().__init__()
		# Load UI from file
		loadUi('ui/mainwindow.ui', self)
		# Add AerialWare
		self.content = AerialWareWidget()
		self.centralWidget().layout().addWidget(self.content)

class AerialWareWidget(QWidget):
	"""Core of AerialWare. Place it into your application, and you're good to go.

	Constructor args:
		getResultsAfterCompletion -- signifies if it's needed to get results. Already set to True if you use AerialWare as a module.
	Methods:
		!!! Use ONLY methods listed below !!!
		getResults() -- returns dictionary with results if user is done. Returns None otherwise.
	Signals:
		done -- emitted when user is done with the program. Call getResults() in your slot to get results.
	"""
	
	done = pyqtSignal()

	def __init__(self, getResultsAfterCompletion = False):
		super().__init__()
		# Set flag to return results after user is done with the program.
		self.getResultsAfterCompletion = getResultsAfterCompletion
		# Load UI from file
		loadUi('ui/form.ui', self)
		# Create scene
		self.scene = QCustomScene()
		self.Image.setScene(self.scene)

		self.errorsAreHere = False  # Used to indicate step with errors for changing languages

		# Load languages
		lang_dir = os.path.dirname(__file__) + "/lang/"
		for lang in os.listdir(lang_dir):
			if os.path.isfile(lang_dir + lang):
				lg = importlib.import_module("lang." + os.path.splitext(lang)[0])
				name = lg.getName()
				self.comboLang.addItem(name, lg)
		self.comboLang.currentIndexChanged.connect(self.changeLanguage)
		# Use English by default
		index = self.comboLang.findText("English")
		self.comboLang.setCurrentIndex(index)
		self.changeLanguage()

		# Set default zoom value
		self.zoom = 100.0

		# Initialize step 1
		self.stepOne()

	##################
	def stepOne(self):
		"""Step 1 -- loading image, connecting events to controls
		"""
		self.disableItems()
		# If user opened image with this program
		try:
			self.loadImage(argv[1])
		except IndexError:
			self.loadImage(os.path.dirname(__file__) + "/ui/img/logo.png")
		# Connect events
		self.btnOpenImage.clicked.connect(self.loadImage)
		self.btnNext.clicked.connect(self.stepTwo)
		self.btnIncreaseZoom.clicked.connect(self.increaseZoom)
		self.btnDecreaseZoom.clicked.connect(self.decreaseZoom)
		self.editZoom.textEdited.connect(self.setZoom)

	def loadImage(self, path = None):
		# Open file dialog and get path or try to use user's path
		if path == None or not path:
			file = QFileDialog.getOpenFileName(self, self.special["open_image"], "", self.special["images"] + "(*.jpg *.jpeg *.png *.bmp);;" + self.special["all_files"] + " (*)")[0]
		else:
			file = path

		# Create a pixmap from file
		img = QPixmap(file)

		# Check if it's an image and draw it or raise error message
		if not img.isNull():
			self.scene.clear()
			item = QGraphicsPixmapItem(img)
			self.scene.addItem(item)
			self.height = img.height()
			self.width = img.width()
			self.enableItems()
		elif file != "":
			self.disableItems()
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setWindowTitle(self.special["invalid_image_title"])
			msg.setText(self.special["invalid_image"])
			msg.exec_()

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
		self.errorsAreHere = True # Used to indicate step with errors for changing languages
		# Validate data
		def setError(s):
			"""Formats string for displaying
			"""
			self.lblDataError.setText("<html><head/><body><div style='font-size: 12pt'>" + self.special["err_data"] + s + "</div></body></html>")

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
			setError(self.special["err_numeric"])
			return

		# Check for metric errors
		if xD <= 0 or yD <= 0:
			setError(self.special["err_delimiters"])
			return

		# And calculate px / deg ratio, i.e. deg * (px / deg) = px
		try:
			self.xDTop = int(self.width / abs(xTL - xTR) * xD)
			self.xDBottom = int(self.width / abs(xBL - xBR) * xD)
			self.yDLeft = int(self.height / abs(yTL - yBL) * yD)
			self.yDRight = int(self.height / abs(yTR - yBR) * yD)
		except ZeroDivisionError:
			setError(self.special["err_corners"])
			return

		errors = ""
		if self.xDTop > self.width:
			errors += self.special["err_long_top"] + "<br>"
		if self.xDBottom > self.width:
			errors += self.special["err_long_bottom"] + "<br>"
		if self.yDLeft > self.height:
			errors += self.special["err_lat_left"] + "<br>"
		if self.yDRight > self.height:
			errors += self.special["err_lat_right"] + "<br>"

		if errors != "":
			setError(self.special["err_sides"] + "<br>" + errors)
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
			setError(self.special["err_points"])
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
		if self.getResultsAfterCompletion:
			nextText = self.special["done"]
		else:
			nextText = self.special["save"]
		self.btnNext.setText(nextText)
		self.btnNext.disconnect()
		self.btnNext.clicked.connect(self.save)
		self.errorsAreHere = False # Used to indicate step with errors for changing languages

	##################

	def save(self):
		"""If AerialWare has been used as a module emits signal 'done'. Saves user results into SVG otherwise.
		"""
		if self.getResultsAfterCompletion:
			self.done.emit()
			return

		self.disableItems()

		file = QFileDialog.getSaveFileName(self, self.special["save_file"], "", self.special["vector_image"] + " (*.svg)")[0]
		if file == "":
			self.enableItems()
			return

		rect = self.scene.sceneRect()
		gen = QSvgGenerator()
		gen.setFileName(file)
		gen.setSize(rect.size().toSize())
		gen.setViewBox(rect)
		gen.setTitle("Flight paths generated by AerialWare")
		gen.setDescription(gen.title())

		# Notice: painting will temporarily freeze application because QGraphicsScene::render is not thread safe.
		# Don't try putting this into python's threads and QThread, doesn't work, I've tried, trust me XD.
		painter = QPainter(gen)
		self.scene.render(painter)
		painter.end()

		self.enableItems()

	def getResults(self):
		"""Returns results of the program in a dictionary.
		Results currently are:
			scene -- QCustomGraphicsScene. Contains image and flight paths
		"""
		if self.getResultsAfterCompletion:
			return {
				"scene": self.scene
			}
		return None

	##################
	
	# Misc stuff
	def enableItems(self):
		"""Enables controls
		"""
		self.scene.setEnabled(True)
		self.editZoom.setEnabled(True)
		self.btnDecreaseZoom.setEnabled(True)
		self.btnIncreaseZoom.setEnabled(True)
		self.btnNext.setEnabled(True)

	def disableItems(self):
		"""Disables controls
		"""
		self.scene.setEnabled(False)
		self.editZoom.setEnabled(False)
		self.btnDecreaseZoom.setEnabled(False)
		self.btnIncreaseZoom.setEnabled(False)
		self.btnNext.setEnabled(False)

	def changeLanguage(self):
		"""Changes app language.
		Uses unified interface, but doesn't check if file is valid language pack. Please refer to any default language as an example if you want to make translations.
		"""
		# Get language
		lang = self.comboLang.currentData()

		# Get special data
		self.special = lang.getSpecial()
		
		# Change text of labels and buttons
		controls = lang.getControls()
		for widget in controls:
			getattr(self, widget).setText(controls[widget])
		
		# Change text of task labels
		start = "<html><head/><body><div style='font-size: 12pt;'>"
		end = "</div></body></html>"

		task = lang.getTaskOne()
		self.lblTask_1.setText(start + f"""
			<p style='font-size: 14pt; text-align: center;'><b>{task["heading"]}</b></p>
			<p><b>{task["heading_about"]}</b></p>
			<p>{task["about_1"]}</p>
			<p>{task["about_2"]}</p>
			<p><b>{task["working_title"]}</b></p>
			<p>{task["working"]}</p>
			<p><b>{task["this_step_bold"]}</b>{task["this_step"]}</p>
			<p><b>{task["note_bold"]}</b>{task["note"]}</p>
			""" + end )

		task = lang.getTaskTwo()
		self.lblTask_2.setText(start + f"""
			<p><b>{task["set_title"]}</b></p>
			<ul>
				<li>{task["coordinates"]}</li>
				<li>{task["delimiters"]}</li>
			</ul>
		""" + end)
		
		task = lang.getTaskThree()
		if self.getResultsAfterCompletion:
			btnText = self.special["done"]
		else:
			btnText = self.special["save"]

		self.lblTask_3.setText(start + f"""
			<p>{task["intro"]}<b>{task["click_bold"]}</b></p>
			<p>{task["path"]}</p>
			<p>{task["save_1"]} <b>\"{btnText}\"</b>{task["save_2"]}</p>
			<p><b>{task["legend_title"]}</b></p>
			<ul>
				<li><span style="color: red;">{task["red"]}</span>{task["line_1"]}<span style="color: green;">{task["green"]}</span>{task["line_2"]}</li>
				<li><b>{task["dashed_bold"]}</b>{task["line_3"]}</li>
			</ul>
			<p><b>{task["note_bold"]}</b>{task["note"]} ¯\_(ツ)_/¯</p>
		""" + end)

		if self.errorsAreHere and self.lblDataError.text() != "":
			self.stepThree()
		
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
			self.editZoom.setText(str(self.zoom * 100))
			self.setZoom()
			return
		self.Image.resetTransform()
		self.Image.scale(value, value)
		self.zoom = value
		
##################

# Custom subclasses

class QCustomScene(QGraphicsScene):
	"""Subclass of QGraphicsScene. Does a lot of program-specific stuff.
	Works with custom polygons, re-implements selection, draws paths.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs) 
		self.customSelectedItems = []
		self.enabled = True

	def setEnabled(self, enabled):
		"""Enables or disables scene from responding to mouse events.
		"""
		self.enabled = enabled

	def mousePressEvent(self, event):
		"""Checks and unchecks squares under cursor if RMB has been pressed
		"""
		if not self.enabled:
			return
			
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
		self.drawPaths()

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
		pen.setCosmetic(True)
		# Pen for turning lines
		pen2 = QPen(color)
		pen2.setWidth(2)
		pen2.setStyle(Qt.DashLine)
		pen2.setDashOffset(2)
		pen2.setCosmetic(True)

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
	"""Represents cell of a grid. Contains program-specific methods.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Set appearance
		pen = QPen(QColor(30, 30, 255))
		pen.setWidth(2)
		pen.setCosmetic(True)
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
		"""Returns dictionary with row and column
		"""
		return {
			"row": self.row,
			"col": self.col
		}


class AerialWare():
	"""Runs AerialWare. Work with program only through this class.

	AerialWare can be used in two modes:
		1. Standalone -- used by defalt. Check runStandalone() method to get more information. AerialWare doesn't communicate with your program in any way in this mode.
		2. Module -- use this to integrate AerialWare into your program.

	Usage in module mode:
		1. Create instance of this class and call getQWidget():
			self.program = AerialWare().getQWidget()
		2. When user is done AerialWare will emit corresponding signal. Connect 'done' signal to your slot:
			self.program.done.connect(self.slot)
		3. Get results. In your slot call getResults() method of the program:
			def slot(self):
				results = self.program.getResults()
				# Process results
				...
		4. Close the program. It is your responsibility to do this. You may want to leave the program and re-process results so user will not go through the whole stuff again.
	"""

	def __init__(self):
		pass
	
	def runStandalone(self):
		"""Runs AerialWare as standalone application, in window and stuff.
		"""
		# Create an instance of QApplication
		app = QApplication(argv)
		# Create an instance of our Window class
		window = Window()
		# Show window
		window.show()
		# Execute app and also write action for exiting
		exit(app.exec_())

	def getQWidget(self):
		"""Returns AerialWare as QWidget.
		"""
		return AerialWareWidget(True)

if __name__ == '__main__':
	AerialWare().runStandalone()
