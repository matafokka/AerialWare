# I've tried to make it look like table.
# In the left column we have variables. Don't touch it.
# In the right column we have text. It goes as user progress through program.
# But if you're unsure what is specific line stands for, open the program and find the same text.
# And please don't change positions of lines, so other translators can work with your files like with others.

# Variables				Text

name = 					"English" # Name of this language

# Stuff for captions and controls
lblZoom =				"Zoom (%):"
btnNext =				"Next >>"
btnOpenImage =			"Open image"
lblCorner =				"Corner"
lblLongtitude =			"Longtitude"
lblLatitude =			"Latitude"
lblTopLeft =			"Top left:"
lblTopRight =			"Top right:"
lblBottomLeft =			"Bottom left:"
lblBottomRight =		"Bottom right:"
lblDelimiters =			"Delimiters:"

# This stuff is used in code itself.
# There are errors, popups and some other dynamically generated items.
openImage =				"Open image"
images =				"Images"
allFiles =				"All files"
invalidImageTitle =		"AerialWare - Invalid image"
invalidImage =			"It's not an image. Please open a valid image."
errData =				"Can't procede "
errNumeric =			"some fields contains non-numeric values. Please recheck everything and click \"Next\" again."
errDelimiters =			"delimiters should be more than zero. Please set correct delimiters."
errCorners =			"some given corners are at the same point. Please recheck every coordinate."
errLongTop =			"Longtitude delimiter is less than given size of top of the image. Please check longtitude of top corners."
errLongBottom =			"Longtitude delimiter is less thagiven n size of bottom of the image. Please check longtitude of bottom corners."
errLatLeft =			"Latitude delimiter is less than given size of left of the image. Please check latitude of left corners."
errLatRight =			"Latitude delimiter is less than diven size of right of the image. Please check latitude of right corners."
errSides =				"something's wrong with given data:"
errPoints =				"can't generate grid. I dont even wanna know how you managed to get this error. Please recheck everything and try again."
warningCoordinates =	"Given coordinates are forming 8-shaped figure. You may get wrong results. Do you want to proceed?"
saveFile =				"Save file"
vectorImage =			"Vector image"
save =					"Save"
done =					"Done"

# Description of Step 1
heading =				"PLEASE READ"
headingAbout =			"About AerialWare"
about1 =				"AerialWare calculates and draws flight paths for aerial photography."
about2 =				"Main feature of AerialWare is coordinate system transformation instead of image transformation. It lets you see your image without distortions caused by transformation."
workingTitle =			"Working with a program"
working =				"Proccess is divided into 3 steps and shouldn't take a lot of time (please check note below). Follow instructions and click \"Next\" to go to the next step."
thisStepBold =			"For this step "
thisStep =				"open image for which operations should be done."
noteStep1Bold =			"Note: "
noteStep1 =				"you can save only final results, so please plan your time."

# Captions for Step 2
setTitle =				"Set following information:"
coordinates =			"Coordinates of image corners in Geographic system as fraction."
delimiters =			"Latitude and longtitude of grid delimiters."

# Description of Step 3
intro =					"We drew some squeres on your image. Please choose those that needed to be captured. To do so, aim on square and "
clickBold =				"click Right Mouse Button."
path =					"Path will be drawn automaticallty after you click on square."
save1 =					"When you're done click "
save2 =					" to save your results. You will get image and report under the same name but report will have .csv extension. You can open it in any spreadsheet program like Microsoft Excel or LibreOffice Spreadsheets."
legendTitle =			"Legend:"
red =					"Red"
line1 =					" line represents flight path by meridians, "
green =					"green one"
line2 =					" -- by parallels."
dashedBold =			"Dashed parts"
line3 =					" represents plane turns between meridians or parallels."
noteStep3Bold =			"Note: "
noteStep3 =				"program may freeze while saving a large file, we can't do anything about that"

# Stuff for report
repCornersDescription =	"Coordinates of corners of image:"
repPoint =				"Point"
repTotalWithTurns =		"Approximate total path lengths (including turns), deg:"
repTotalWithoutTurns =	"Total path lengths (without turns), deg:"
repByMeridians =		"By meridians:"
repByHorizontals =		"By horizontals:"
repBetterFlyBy =		"Better fly by:"
repFlyMeridians =		"Meridians"
repFlyHorizontals =		"Horizontals"
repFlyEqual =			"Up to you, paths are equal."
repMeridianPoints =		"Flight points by meridians:"
repHorizontalPoints =	"Flight points by horizontals:"
