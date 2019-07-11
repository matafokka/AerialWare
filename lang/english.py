def getName():
	return "English"

def getControls():
	return {
		"lblZoom":			"Zoom (%):",
		"btnNext":			"Next >>",
		"btnOpenImage":		"Open image",
		"lblCorner":		"Corner",
		"lblLongtitude":	"Longtitude",
		"lblLatitude":		"Latitude",
		"lblTopLeft":		"Top left:",
		"lblTopRight":		"Top right:",
		"lblBottomLeft":	"Bottom left:",
		"lblBottomRight":	"Bottom right:",
		"lblDelimiters":	"Delimiters:"
	}

def getSpecial():
	return {
		"open_image":		"Open image",
		"images":			"Images",
		"all_files":		"All files",
		"invalid_image_title": "AerialWare - Invalid image",
		"invalid_image":	"It's not an image. Please open a valid image.",
		"err_data":			"Can't procede, ",
		"err_numeric":		"some fields contains non-numeric values. Please recheck everything and click \"Next\" again.",
		"err_delimiters":	"delimiters should be more than zero. Please set correct delimiters.",
		"err_corners":		"some given corners are at the same point. Please recheck every coordinate.",
		"err_long_top":		"Longtitude delimiter is less than given size of top of the image. Please check longtitude of top corners.",
		"err_long_bottom":	"Longtitude delimiter is less thagiven n size of bottom of the image. Please check longtitude of bottom corners.",
		"err_lat_left":		"Latitude delimiter is less than given size of left of the image. Please check latitude of left corners.",
		"err_lat_right":	"Latitude delimiter is less than diven size of right of the image. Please check latitude of right corners.",
		"err_sides":		"something's wrong with given data:",
		"err_points":		"can't generate grid. I dont even wanna know how you managed to get this error. Please recheck everything and try again.",
		"save_file":		"Save file",
		"vector_image":		"Vector image",
		"save":				"Save",
		"done":				"Done"
	}

def getTaskOne():
	return {
		"heading":			"PLEASE READ",
		"heading_about":	"About AerialWare",
		"about_1":			"AerialWare calculates and draws flight paths for aerial photography.",
		"about_2":			"Main feature of AerialWare is coordinate system transformation instead of image transformation. It lets you see your image without distortions caused by transformation.",
		"working_title":	"Working with a program",
		"working":			"Proccess is divided into 3 steps and shouldn't take a lot of time (please check note below). Follow instructions and click \"Next\" to go to the next step.",
		"this_step_bold":	"For this step ",
		"this_step":		"open image for which operations should be done.",
		"note_bold":		"Note: ",
		"note":				"you can save only final results, so please plan your time."
	}

def getTaskTwo():
	return {
		"set_title":		"Set following information:",
		"coordinates":		"Coordinates of image corners in Geographic system as fraction.",
		"delimiters":		"Latitude and longtitude of grid delimiters."
	}

def getTaskThree():
	return {
		"intro":			"We drew some squeres on your image. Please choose those that needed to be captured. To do so, aim on square and ",
		"click_bold":		"click Right Mouse Button.",
		"path":				"Path will be drawn automaticallty after you click on square.",
		"save_1":			"When you're done click ",
		"save_2":			" to save your results.",
		"legend_title":		"Legend:",
		"red":				"Red",
		"line_1":			" line represents flight path by meridians, ",
		"green":			"green",
		"line_2":			" -- by parallels.",
		"dashed_bold":		"Dashed parts",
		"line_3":			" represents plane turns between meridians or parallels.",
		"note_bold":		"Note: ",
		"note":				"program may freeze when saving a large file, we can't do anything about that"
	}
