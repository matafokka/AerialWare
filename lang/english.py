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
lblLongitude =			"Longitude"
lblLatitude =			"Latitude"
lblTopLeft =			"Top left:"
lblTopRight =			"Top right:"
lblBottomLeft =			"Bottom left:"
lblBottomRight =		"Bottom right:"
lblDelimiters =			"Delimiters:"
lblDesiredRes =			"Desired resolution (m/px):"
lblRes =				"Calculated resolution of camera (px):"
lblHeight =				"Flight height (m):"
lblFocal =				"Focal length (mm):"

# This stuff is used in code itself.
# There are errors, popups and some other dynamically generated items.
openImage =				"Open image"
images =				"Images"
allFiles =				"All files"
invalidImageTitle =		"AerialWare - Invalid image"
invalidImage =			"It's not an image. Please open a valid image."
errData =				"Can't procede "
errCorners =			"some given corners are at the same point. Please recheck every coordinate."
errLongTop =			"Longitude delimiter is less than given size of top of the image. Please check longitude of top corners."
errLongBottom =			"Longitude delimiter is less thagiven n size of bottom of the image. Please check longitude of bottom corners."
errLatLeft =			"Latitude delimiter is less than given size of left of the image. Please check latitude of left corners."
errLatRight =			"Latitude delimiter is less than diven size of right of the image. Please check latitude of right corners."
errSides =				"something's wrong with given data:"
errPoints =				"can't generate grid. I dont even wanna know how you managed to get this error. Please recheck everything and try again."
warningCoordinates =	"Given coordinates are forming 8-shaped figure. You may get wrong results. Do you want to proceed?"
saveFile =				"Save file"
errEmptySelection =		"You haven't selected any square. Please select something."
errSaveBoth =			"You need to save both files. Please select where you want to save the report."
vectorImage =			"Vector image"
table =					"Simple Table"
save =					"Save"
done =					"Done"

# Description of Step 1
heading =				"PLEASE READ"
headingAbout =			"About AerialWare"
about1 =				"AerialWare calculates and draws flight paths for aerial photography."
about2 =				"Main feature of AerialWare is coordinate system transformation instead of image transformation. It lets you see your image without distortions caused by transformation."
workingTitle =			"Working with a program"
working =				"Proccess is divided into 4 steps and shouldn't take a lot of time (please check note below). Follow instructions and click \"Next\" to go to the next step."
thisStepBold =			"For this step "
thisStep =				"open image for which operations should be done."
noteStep1Bold =			"Note: "
noteStep1 =				"you can save only final results, so please plan your time."

# Captions for Step 2
setTitle =				"Please set following information:"
coordinates =			"Coordinates of image corners in Geographic system as fraction."
delimiters =			"Latitude and longitude of grid delimiters."

# Description of Step 3
intro =					"We drew some squeres on your image. Please choose those that needed to be captured. To do so, aim on square and "
clickBold =				"click Right Mouse Button."
path =					"Path will be drawn automaticallty after you click on square."
legendTitle =			"Legend:"
red =					"Red"
line1 =					" line represents flight path by meridians, "
green =					"green one"
line2 =					" -- by parallels."
dashedBold =			"Dashed parts"
line3 =					" represents plane turns between meridians or parallels."

# Description for Step 4
s4Text1P1 =				"You need a camera that can capture "
s4Text1P2 =				" meters terrain. Please enter resolution (meters in pixel) you want to have, so we can calculate needed resolution of camera."
s4Text2 =				"Please enter needed flight height so we can calculate focal length of a camera."
s4Save =				"When you're done click \"Save\" to save your results. Report will have .csv extension. You can open it in any spreadsheet program like Microsoft Excel or LibreOffice Spreadsheets."
s4Done =				"When you're done click \"Done\"."
noteStep4Bold =			"Note: "
noteStep4 =				"program may freeze while saving a large file. Please wait until program unfreeze or you will lose results. We can't do anything about it"

# Stuff for report
repCornersDescription =	"Coordinates of corners of image:"
repPoint =				"Point"
repTotalWithTurns =		"Approximate total path lengths (including turns), m:"
repTotalWithoutTurns =	"Total path lengths (without turns), m:"
repByMeridians =		"By meridians:"
repByHorizontals =		"By horizontals:"
repBetterFlyBy =		"Better fly by:"
repFlyMeridians =		"Meridians"
repFlyHorizontals =		"Horizontals"
repFlyEqual =			"Up to you, paths are equal."
repAerialParams =		"Aerial parameters"
repArea =				"Maximum area to be captured (m):"
repMeridianPoints =		"Flight points by meridians:"
repHorizontalPoints =	"Flight points by horizontals:"
