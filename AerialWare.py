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
from PyQt5.uic import loadUi # For loading ui files
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
		self.scene = _QCustomScene()
		self.Image.setScene(self.scene)
		# Use antialiasing
		self.Image.setRenderHint(QPainter.Antialiasing)

		self.errorsAreHere = False # Used to indicate step with errors for changing languages
		self.endIsHere = False # Used to indicate where Next button should have "Save" or "Done" caption.

		# Load languages

		langDir = os.path.dirname(__file__) + "/lang/"
		for lang in os.listdir(langDir):
			ext = os.path.splitext(lang)
			if os.path.isfile(langDir + lang) and ext[1] == ".py":
				lg = importlib.import_module("lang." + ext[0])
				name = lg.name
				self.comboLang.addItem(name, lg)
		self.comboLang.currentIndexChanged.connect(self.__changeLanguage)
		
		# Use English by default. Use it as fallback language. If it's not found, display error message and exit.
		index = self.comboLang.findText("English")
		if index == -1:
			QMessageBox(QMessageBox.Critical, "AerialWare - Error", "English localization not found. It should be in file " + langDir + "english.py. AerialWare uses it as base localization. Please, download AerialWare again.").exec()
			exit()

		self.comboLang.setCurrentIndex(index)
		self.lang = _LanguageChanger(self.comboLang.currentData()) # Create language changer
		self.__changeLanguage()

		# Set default zoom value
		self.zoom = 100.0

		# Initialize step 1
		self.__stepOne()

	##################
	def __stepOne(self):
		"""Step 1 -- loading image, connecting events to controls
		"""
		self.__disableItems()
		# If user opened image with this program
		try:
			self.__loadImage(argv[1])
		except IndexError:
			self.__loadImage(os.path.dirname(__file__) + "/ui/img/logo.png")
		# Connect events
		self.btnOpenImage.clicked.connect(self.__loadImage)
		self.btnNext.clicked.connect(self.__stepTwo)
		self.btnIncreaseZoom.clicked.connect(self.__increaseZoom)
		self.btnDecreaseZoom.clicked.connect(self.__decreaseZoom)
		self.editZoom.textEdited.connect(self.__setZoom)

	def __loadImage(self, path = None):
		# Open file dialog and get path or try to use user's path
		if path == None or not path:
			file = QFileDialog.getOpenFileName(self, self.lang.openImage, "", self.lang.images + "(*.jpg *.jpeg *.png *.bmp);;" + self.lang.allFiles + " (*)")[0]
		else:
			file = path

		# Create a pixmap from file
		img = QPixmap(file)

		# Check if it's an image and draw it or raise error message
		if not img.isNull():
			self.scene.clear()
			item = QGraphicsPixmapItem(img)
			self.height = img.height()
			self.width = img.width()
			self.scene.addItem(item)
			self.__enableItems()
		elif file != "":
			self.__disableItems()
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setWindowTitle(self.lang.invalidImageTitle)
			msg.setText(self.lang.invalidImage)
			msg.exec_()

	##################

	def __stepTwo(self):
		"""Step 2 -- Needed only for first click. Step 3 does all the job.
		"""
		self.__turnPage()
		self.btnNext.disconnect()
		self.btnNext.clicked.connect(self.__stepThree)

	##################

	def __stepThree(self):
		"""Step 3 -- Do basically everything.
		"""
		self.errorsAreHere = True # Used to indicate step with errors for changing languages
		# Validate data
		def setError(e):
			"""Displays string e.
			"""
			self.lblDataError.setText("<html><head/><body><div style='font-size: 12pt'>" + self.lang.errData + e + "</div></body></html>")

		# Try to read data. We need to create fields, because this will be used later in other functions.
		try:
			self.xTL = float(self.xTopLeft.text())
			self.xTR = float(self.xTopRight.text())
			self.xBL = float(self.xBottomLeft.text())
			self.xBR = float(self.xBottomRight.text())

			self.yTL = float(self.yTopLeft.text())
			self.yTR = float(self.yTopRight.text())
			self.yBL = float(self.yBottomLeft.text())
			self.yBR = float(self.yBottomRight.text())

			self.xD = float(self.xDelimiter.text())
			self.yD = float(self.yDelimiter.text())
		except:
			# Write error message
			setError(self.lang.errNumeric)
			return

		# Check for metric errors
		if self.xD <= 0 or self.yD <= 0:
			setError(self.lang.errDelimiters)
			return

		# Convert delimiters to pixels.
		# Value of another coordinate doesn't matter.
		# If you'll draw a random line and draw crossing lines parallel to one of axes with same distance between these lines by another axis, you'll split your random line into equal pieces.
		# See for yourself:
		# Y
		# ^ ___\_____
		# | ____\____
		# | _____\___
		# |       \
		# |-----------> X
		# You can try it on paper or prove this "theorem" doing some math.
		try:
			self.xDTop = self.width / abs(self.xTL - self.xTR) * self.xD
			self.xDBottom = self.width / abs(self.xBL - self.xBR) * self.xD
			self.yDLeft = self.height / abs(self.yTL - self.yBL) * self.yD
			self.yDRight = self.height / abs(self.yTR - self.yBR) * self.yD
		except ZeroDivisionError:
			setError(self.lang.errCorners)
			return
		
		# Now do the same stuff, but find how much pixels in one degree.
		# We won't find absolute value for subtraction because axes of image in geographic system may be not codirectional to axes of image in Qt system.
		self.topX = (self.xTR - self.xTL) / self.width
		self.bottomX = (self.xBR - self.xBL) / self.width
		self.leftY = (self.yTL - self.yBL) / self.height
		self.rightY = (self.yTR - self.yBR) / self.height

		# Sides of image in geographic system
		self.top = QLineF(self.xTL, self.yTL, self.xTR, self.yTR)
		self.bottom = QLineF(self.xBL, self.yBL, self.xBR, self.yBR)
		self.left = QLineF(self.xTL, self.yTL, self.xBL, self.yBL)
		self.right = QLineF(self.xTR, self.yTR, self.xBR, self.yBR)

		errors = ""
		if self.xDTop > self.width:
			errors += self.lang.errLongTop + "<br>"
		if self.xDBottom > self.width:
			errors += self.lang.errLongBottom + "<br>"
		if self.yDLeft > self.height:
			errors += self.lang.errLatLeft + "<br>"
		if self.yDRight > self.height:
			errors += self.lang.errLatRight + "<br>"

		if errors != "":
			setError(self.lang.errSides + "<br>" + errors)
			return
		
		# Check if given coordinates form 8-shaped figure
		if (self.xTL > self.xTR and self.xBL < self.xBR) or (self.xTL < self.xTR and self.xBL > self.xBR) or (self.yTL > self.yBL and self.yTR < self.yBR) or (self.yTL < self.yBL and self.yTR > self.yTL):
			choice = QMessageBox(QMessageBox.Warning, "AerialWare", self.lang.warningCoordinates, QMessageBox.Yes | QMessageBox.No).exec()
			if choice == QMessageBox.No:
				return

		self.__turnPage()

		# Draw grid

		# Set points for grid
		# Points will look like:
		# [point, point, ...],
		# [point, point, ...], ...
		pointRows = []
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
				point = QPointF()
				QLineF.intersect(
					QLineF(x1, y1, x2, y2),
					QLineF(x3, y3, x4, y4),
					point
				)
				points.append(point)
				x1 += self.xDTop
				x2 += self.xDBottom
			if points != []:
				pointRows.append(points)
			y3 += self.yDLeft
			y4 += self.yDRight
		
		# If nothing has been added
		if points == []:
			setError(self.lang.errPoints)
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
		while i < len(pointRows):
			j = 1 # Points
			while j < len(pointRows[i]):
				# Add points in following order: top left, top right, bottom right, bottom left
				points = [
					pointRows[i - 1][j - 1],
					pointRows[i - 1][j],
					pointRows[i][j],
					pointRows[i][j - 1]
				]
				# We're assigning self.bounds as parent implicitly, so we shouldn't add polygon to scene by ourselves.
				poly = _QCustomGraphicsPolygonItem(QPolygonF(points), self.bounds)
				poly.setRowCol(i - 1, j - 1)
				j += 1
			i += 1
		# Restore scene geometry
		self.scene.setSceneRect(rect)

		self.__turnPage()
		self.endIsHere = True # Used to indicate where Next button should have "Save" or "Done" caption.
		if self.getResultsAfterCompletion:
			nextText = self.lang.done
		else:
			nextText = self.lang.save
		self.btnNext.setText(nextText)
		self.btnNext.disconnect()
		self.btnNext.clicked.connect(self.__save)
		self.errorsAreHere = False  # Used to indicate step with errors for changing languages

	##################

	def __save(self):
		"""If AerialWare has been used as a module, emits signal 'done'. Saves user results into SVG and makes report otherwise.
		"""
		# Variables for report
		self.pointsMeridian = ""
		self.pointsHorizontal = ""

		# Total lengths of paths. Used in report and methods.
		self.lenMeridian = 0
		self.lenMeridianWithTurns = 0
		self.lenHorizontal = 0
		self.lenHorizontalWithTurns = 0

		# Fields for methods
		self.pathMeridianPointsPx = []
		self.pathMeridianPointsDeg = []
		self.pathMeridianLinesPx = []
		self.pathMeridianLinesWithTurnsPx = []
		self.pathMeridianLinesDeg = []
		self.pathMeridianLinesWithTurnsDeg = []

		self.pathHorizontalPointsPx = []
		self.pathHorizontalPointsDeg = []
		self.pathHorizontalLinesPx = []
		self.pathHorizontalLinesWithTurnsPx = []
		self.pathHorizontalLinesDeg = []
		self.pathHorizontalLinesWithTurnsDeg = []

		# Process each line
		def processLines(lines, isMeridian=False):
			i = 2 # Counter for report
			isEven = False # If current line is even we must swap it's points.
			for line in lines:
				linePx = line.line()
				p1 = linePx.p1()
				p2 = linePx.p2()
				p1Deg = self.pxToDeg(p1.x(), p1.y())
				p2Deg = self.pxToDeg(p2.x(), p2.y())
				lineDeg = QLineF(p1Deg, p2Deg)
				lineLength = lineDeg.length()

				if isMeridian:
					self.pathMeridianLinesWithTurnsPx.append(linePx)
					self.pathMeridianLinesWithTurnsDeg.append(lineDeg)
					self.lenMeridianWithTurns += lineLength
				else:
					self.pathHorizontalLinesWithTurnsPx.append(linePx)
					self.pathHorizontalLinesWithTurnsDeg.append(lineDeg)
					self.lenHorizontalWithTurns += lineLength

				if line.pen().style() == Qt.SolidLine:  # Check if current line doesn't represent turn
					if isEven:
						p1, p2, p1Deg, p2Deg = p2, p1, p2Deg, p1Deg
					
					point = f'"{i - 1}","{p1Deg.x()}","{p1Deg.y()}"\n' + f'"{i}","{p2Deg.x()}","{p2Deg.y()}"\n'
					if isMeridian:
						self.pointsMeridian += point
						self.pathMeridianPointsPx.extend([p1, p2])
						self.pathMeridianPointsDeg.extend([p1Deg, p2Deg])
						self.pathMeridianLinesPx.append(linePx)
						self.pathMeridianLinesDeg.append(lineDeg)
						self.lenMeridian += lineLength
					else:
						self.pointsHorizontal += point
						self.pathHorizontalPointsPx.extend([p1, p2])
						self.pathHorizontalPointsDeg.extend([p1Deg, p2Deg])
						self.pathHorizontalLinesPx.append(linePx)
						self.pathHorizontalLinesDeg.append(lineDeg)
						self.lenHorizontal += lineLength
					isEven = not isEven
					i += 2

		processLines(self.scene.getMeridianLines(), True)
		processLines(self.scene.getHorizontalLines())
		
		if self.getResultsAfterCompletion:
			self.done.emit()
			return

		self.__disableItems()

		# Make report
		pointHeader = f'"{self.lang.repPoint}","{self.lang.lblLatitude}","{self.lang.lblLongtitude}"\n'
		
		if self.lenHorizontalWithTurns > self.lenMeridianWithTurns:
			directionWithTurns = self.lang.repFlyMeridians
		elif self.lenHorizontalWithTurns < self.lenMeridianWithTurns:
			directionWithTurns = self.lang.repFlyHorizontals
		else:
			directionWithTurns = self.lang.repFlyEqual

		if self.lenHorizontal > self.lenMeridian:
			directionWithoutTurns = self.lang.repFlyMeridians
		elif self.lenHorizontal < self.lenMeridian:
			directionWithoutTurns = self.lang.repFlyHorizontals
		else:
			directionWithoutTurns = self.lang.repFlyEqual

		report = (
		f'"{self.lang.repCornersDescription}"\n'
		f'"{self.lang.lblCorner}","{self.lang.lblLongtitude}","{self.lang.lblLatitude}"\n'
		f'"{self.lang.lblTopLeft}","{self.xTL}","{self.yTL}"\n'
		f'"{self.lang.lblTopRight}","{self.xTR}","{self.yTR}"\n'
		f'"{self.lang.lblBottomLeft}","{self.xBL}","{self.yBL}"\n'
		f'"{self.lang.lblBottomRight}","{self.xBR}","{self.yBR}"\n'
		f'"{self.lang.lblDelimiters}","{self.xD}","{self.yD}"\n\n'
		f'"{self.lang.repTotalWithTurns}"\n'
		f'"{self.lang.repByMeridians}","{self.lenMeridianWithTurns}"\n'
		f'"{self.lang.repByHorizontals}","{self.lenHorizontalWithTurns}"\n'
		f'"{self.lang.repBetterFlyBy}","{directionWithTurns}"\n\n'
		f'"{self.lang.repTotalWithoutTurns}"\n'
		f'"{self.lang.repByMeridians}","{self.lenMeridian}"\n'
		f'"{self.lang.repByHorizontals}","{self.lenHorizontal}"\n'
		f'"{self.lang.repBetterFlyBy}","{directionWithoutTurns}"\n\n'
		f'"{self.lang.repMeridianPoints}"\n'
		+ pointHeader + self.pointsMeridian + 
		f'\n"{self.lang.repHorizontalPoints}"\n'
		+ pointHeader + self.pointsHorizontal)

		# Save image
		file = QFileDialog.getSaveFileName(self, self.lang.saveFile, "", self.lang.vectorImage + " (*.svg)")[0]
		if file == "":
			self.__enableItems()
			return
		
		rect = self.scene.sceneRect()
		gen = QSvgGenerator()
		gen.setFileName(file)
		gen.setSize(rect.size().toSize())
		gen.setViewBox(rect)
		gen.setTitle("Flight paths generated by AerialWare")
		gen.setDescription(gen.title())

		# Notice: painting will temporarily freeze application because QGraphicsScene::render is not thread safe.
		# Don't try putting this into python's threads and QThread, doesn't work, I've tried, trust me self.xD
		painter = QPainter(gen)
		self.scene.render(painter)
		painter.end()

		# Save report
		reportFile = open(os.path.splitext(file)[0] + ".csv", "w")
		reportFile.write(report)
		reportFile.close()

		self.__enableItems()

	##################

	# API

	def getPathByMeridiansPointsPx(self):
		"""Returns list with points in pixels representing flight path by meridians.
		Please note: all points are sorted as a plane should fly.
		"""
		return self.pathMeridianPointsPx

	def getPathByMeridiansPointsDeg(self):
		"""Returns list with points in geographic coordinate system representing flight path by meridians.
		Please note: all points are sorted as a plane should fly.
		Looks like: [QPointF(long, lat), QPointF(long, lat), ...]
		"""
		return self.pathMeridianPointsDeg

	def getPathByMeridiansLinesPx(self):
		"""Returns list with lines in pixels coordinates without turns representing flight path by meridians.
		Please note: all points of lines are sorted as a plane should fly.
		"""
		return self.pathMeridianLinesPx
	
	def getPathByMeridiansLinesWithTurnsPx(self):
		"""Returns list with lines in pixels with turns representing flight path by meridians.
		Please note: points of lines are NOT sorted as a plane should fly. You can use even lines, as they're representing turns, to sort things out. Or just get path without turns.
		"""
		return self.pathMeridianLinesWithTurnsPx

	def getPathByMeridiansLinesDeg(self):
		"""Returns list with lines in degrees without turns representing flight path by meridians.
		Please note: all points of lines are sorted as a plane should fly.
		"""
		return self.pathMeridianLinesDeg

	def getPathByMeridiansLinesWithTurnsDeg(self):
		"""Returns list with lines in degrees with turns representing flight path by meridians.
		Please note: points of lines are NOT sorted as a plane should fly. You can use even lines, as they're representing turns, to sort things out. Or just get path without turns.
		"""
		return self.pathMeridianLinesWithTurnsDeg

	# Horizontals
	def getPathByHorizontalsPointsPx(self):
		"""Returns list with points in pixels representing flight path by horizontals.
		"""
		return self.pathHorizontalPointsPx

	def getPathByHorizontalsPointsDeg(self):
		"""Returns list with points in geographic coordinate system representing flight path by horizontals.
		Looks like: [QPointF(long, lat), QPointF(long, lat), ...]
		"""
		return self.pathHorizontalPointsDeg

	def getPathByHorizontalsLinesPx(self):
		"""Returns list with lines in pixels coordinates without turns representing flight path by horizontals.
		"""
		return self.pathHorizontalLinesPx

	def getPathByHorizontalsLinesWithTurnsPx(self):
		"""Returns list with lines in pixels with turns representing flight path by horizontals.
		"""
		return self.pathHorizontalLinesWithTurnsPx

	def getPathByHorizontalsLinesDeg(self):
		"""Returns list with lines in degrees without turns representing flight path by horizontals.
		"""
		return self.pathHorizontalLinesDeg

	def getPathByHorizontalsLinesWithTurnsDeg(self):
		"""Returns list with lines in degrees with turns representing flight path by horizontals.
		"""
		return self.pathHorizontalLinesWithTurnsDeg

	def getPathLengthByMeridians(self):
		"""Returns length of path by meridians without turns.
		"""
		return self.lenMeridian
	
	# Lengths
	def getPathLengthByMeridiansWithTurns(self):
		"""Returns length of path by meridians with turns. This value is approximate.
		"""
		return self.lenMeridianWithTurns

	def getPathLengthByHorizontals(self):
		"""Returns length of path by horizontal without turns.
		"""
		return self.lenHorizontal

	def getPathLengthByHorizontalsWithTurns(self):
		"""Returns length of path by horizontal with turns. This value is approximate.
		"""
		return self.lenHorizontalWithTurns

	def pxToDeg(self, x, y):
		"""Transforms pixel coordinates of point to Geographic coordinate system.
		Args:
			x, y -- X and Y coordinates of point to process.
		Returns:
			QPointF(long, lat) -- longtitude and latitude coordinates of given point
		"""
		# Please check comments in __stepThree() where we converting step in degrees to pixels in order to understand what we're doing here.
		# Convert given coordinates to degrees relative to the sides.
		topX = self.xTL + self.topX * x
		bottomX = self.xBL + self.bottomX * x
		# We subtract because Y and lat are not codirectional by default
		leftY = self.yTL - self.leftY * y
		rightY = self.yTR - self.rightY * y

		# Find another coordinate for each side by drawing straight line with calculated coordinate for both points.
		# Intersection of this line and side will give needed point.
		# Looks like this:
		# Y
		# ^
		# | \ <- This is side
		# |  \
		# |---*-----  <- This line is crossing point relative to the side
		# |    \
		# |     \
		# |------------------> X
		# Containers for points and result.
		top, bottom, left, right, res = QPointF(), QPointF(), QPointF(), QPointF(), QPointF()

		QLineF.intersect(
			QLineF(topX, 0, topX, 1),
			self.top,
			top
		)
		QLineF.intersect(
			QLineF(bottomX, 0, bottomX, 1),
			self.bottom,
			bottom
		)
		QLineF.intersect(
			QLineF(0, leftY, 1, leftY),
			self.left,
			left
		)
		QLineF.intersect(
			QLineF(0, rightY, 1, rightY),
			self.right,
			right
		)

		# We've got coordinates for each side where given point should lie.
		# Let's draw lines throgh them like this:
		#  ________________________
		# |    \                   |
		# |_____\__________________|
		# |      \                 |
		# |_______\________________|
		# Lines are drawn in geographic system, not in pixels.
		# Their intersection will return given point in geographic system.
		QLineF.intersect(
			QLineF(top, bottom),
			QLineF(left, right),
			res
		)
		return res

	##################
	
	# Misc stuff

	def __enableItems(self):
		"""Enables controls
		"""
		self.scene.setEnabled(True)
		self.editZoom.setEnabled(True)
		self.btnDecreaseZoom.setEnabled(True)
		self.btnIncreaseZoom.setEnabled(True)
		self.btnNext.setEnabled(True)

	def __disableItems(self):
		"""Disables controls
		"""
		self.scene.setEnabled(False)
		self.editZoom.setEnabled(False)
		self.btnDecreaseZoom.setEnabled(False)
		self.btnIncreaseZoom.setEnabled(False)
		self.btnNext.setEnabled(False)

	def __changeLanguage(self):
		"""Changes app language. Uses _LanguageChanger, check it's description for more.
		"""
		# Get language
		self.lang.setLanguage(self.comboLang.currentData())

		# Change text of labels and buttons
		self.lblZoom.setText(self.lang.lblZoom)
		self.lblCorner.setText(self.lang.lblCorner)
		self.lblLongtitude.setText(self.lang.lblLongtitude)
		self.lblLatitude.setText(self.lang.lblLatitude)
		self.lblTopLeft.setText(self.lang.lblTopLeft)
		self.lblTopRight.setText(self.lang.lblTopRight)
		self.lblBottomLeft.setText(self.lang.lblBottomLeft)
		self.lblBottomRight.setText(self.lang.lblBottomRight)
		self.lblDelimiters.setText(self.lang.lblDelimiters)
		self.btnOpenImage.setText(self.lang.btnOpenImage)

		# Change text of task labels
		start = "<html><head/><body><div style='font-size: 12pt;'>"
		end = "</div></body></html>"
		
		self.lblTask1.setText(start + f"""
			<p style='font-size: 14pt; text-align: center;'><b>{self.lang.heading}</b></p>
			<p><b>{self.lang.headingAbout}</b></p>
			<p>{self.lang.about1}</p>
			<p>{self.lang.about2}</p>
			<p><b>{self.lang.workingTitle}</b></p>
			<p>{self.lang.working}</p>
			<p><b>{self.lang.thisStepBold}</b>{self.lang.thisStep}</p>
			<p><b>{self.lang.noteStep1Bold}</b>{self.lang.noteStep1}</p>
			""" + end)
			
		self.lblTask2.setText(start + f"""
			<p><b>{self.lang.setTitle}</b></p>
			<ul>
				<li>{self.lang.coordinates}</li>
				<li>{self.lang.delimiters}</li>
			</ul>
		""" + end)
		
		if self.getResultsAfterCompletion:
			btnText = self.lang.done
		else:
			btnText = self.lang.save

		if self.endIsHere:
			self.btnNext.setText(btnText)
		else:
			self.btnNext.setText(self.lang.btnNext)

		self.lblTask3.setText(start + f"""
			<p>{self.lang.intro}<b>{self.lang.clickBold}</b></p>
			<p>{self.lang.path}</p>
			<p>{self.lang.save1} <b>\"{btnText}\"</b>{self.lang.save2}</p>
			<p><b>{self.lang.legendTitle}</b></p>
			<ul>
				<li><span style="color: red;">{self.lang.red}</span>{self.lang.line1}<span style="color: green;">{self.lang.green}</span>{self.lang.line2}</li>
				<li><b>{self.lang.dashedBold}</b>{self.lang.line3}</li>
			</ul>
			<p><b>{self.lang.noteStep3Bold}</b>{self.lang.noteStep3} ¯\_(ツ)_/¯</p>
		""" + end)

		if self.errorsAreHere and self.lblDataError.text() != "":
			self.__stepThree()
		
	def __turnPage(self):
		"""Turns page of "Steps"
		"""
		self.Steps.setCurrentIndex(self.Steps.currentIndex() + 1)

	def __increaseZoom(self):
		"""Zooms image in
		"""
		value = float(self.editZoom.text()) + 10
		self.editZoom.setText(str(value))
		self.__setZoom()

	def __decreaseZoom(self):
		"""Zooms image out
		"""
		value = float(self.editZoom.text()) - 10
		if value >= 10:
			self.editZoom.setText(str(value))
			self.__setZoom()

	def __setZoom(self):
		"""Sets zoom
		"""
		try:
			value = float(self.editZoom.text()) * 0.01
		except ValueError:
			self.editZoom.setText(str(self.zoom * 100))
			self.__setZoom()
			return
		self.Image.resetTransform()
		self.Image.scale(value, value)
		self.zoom = value
		
##################

# Custom classes

class _LanguageChanger():
	"""Class for loading languages.
	Please set fallback language or this won't work.
	Please refer to any default language as an example if you want to make translations.
	"""
	def __init__(self, fallback = None):
		self.fallback = fallback

	def setFallback(self, fallback):
		"""Sets fallback language.
		"""
		self.fallback = fallback

	def setLanguage(self, lang):
		"""Sets current language.
		Basically writes variables from file to it's fields. If given language is different from fallback, sets fallback first to prevent any errors.
		"""
		if lang.name != self.fallback.name:
			self.setLanguage(self.fallback)
		vs = lang.__dict__
		for k in vs:
			if k[0] != "_":
				setattr(self, k, vs[k])

class _QCustomScene(QGraphicsScene):
	"""Subclass of QGraphicsScene. Does a lot of program-specific stuff.
	Works with custom polygons, re-implements selection, draws paths.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs) 
		self.customSelectedItems = []
		self.rowLines = []
		self.colLines = []
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

		# Find item at selected position. QGraphicsScene::itemAt() uses bounding rectangle instead of shape. And if user clicks on line, it'll return the line.
		# So the only solution is to parse all objects and find which one contains point user clicked at.
		selected = None
		click = event.scenePos()
		for item in self.items():
			if isinstance(item, _QCustomGraphicsPolygonItem) and item.shape().contains(click):
				selected = item
				break

		if selected == None:
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

	def getMeridianLines(self):
		return self.colLines
	
	def getHorizontalLines(self):
		return self.rowLines

	def drawPaths(self):
		"""Draws both flight path
		"""
		# Remove existing lines
		for item in self.items():
			if isinstance(item, QGraphicsLineItem):
				self.removeItem(item)
		self.rowLines, self.colLines = [], []
		# Draw paths
		items = self.selectedItems()
		self.drawPath(items, True)
		self.drawPath(items, False)
		self.update()
	
	def drawPath(self, items, useRows):
		"""Draws one flight path
		Args
		items -- squares.
		useRows:
			True -- go by rows
			False -- go by cols
		"""
		if useRows:
			way = "row"
			sortSecond = "col"
			oldSide = "left"
			newSide = "right"
			color = QColor(255, 10, 10)
		else:
			way = "col"
			sortSecond = "row"
			oldSide = "top"
			newSide = "bottom"
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
		items.sort(key=lambda item: item.getRowCol()[sortSecond])
		items.sort(key=lambda item: item.getRowCol()[way])

		def addItem(item):
			self.addItem(item)
			if useRows:
				self.rowLines.append(item)
			else:
				self.colLines.append(item)

		# Draw lines
		newPos = True # Shows if we're will be at new col/row at next iteration
		prevLine = None # Previously drawn line
		isLastPointReversed = False # Shows from which end draw turning line
		for i in range(len(items)):
			item = items[i]
			if newPos:
				side1 = item.getSides()[oldSide]
				newPos = False
			pos = item.getRowCol()[way]
			try:
				nextPos = items[i + 1].getRowCol()[way]
			except:
				nextPos = pos + 1
			if pos != nextPos:
				side2 = item.getSides()[newSide]
				lineF = QLineF(side1, side2)
				line = QGraphicsLineItem(lineF)
				line.setPen(pen)
				addItem(line)
				newPos = True
				if prevLine != None:
					if isLastPointReversed:
						start = prevLine.p2()
						end = side2
					else:
						start = prevLine.p1()
						end = side1
					newLine = QGraphicsLineItem(QLineF(start, end))
					newLine.setPen(pen2)
					addItem(newLine)
				isLastPointReversed = not isLastPointReversed
				prevLine = lineF


class _QCustomGraphicsPolygonItem(QGraphicsPolygonItem):
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
				# Process results
				# ...
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
