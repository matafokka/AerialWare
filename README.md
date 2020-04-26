# AerialWare
AerialWare is a software for designing aerial photography.

# About AerialWare
AerialWare is a software for designing aerial photography.

AerialWare automates a lot of things and gives you an image with grid and report with some useful calculated stuff.

Main feature of AerialWare is transformation of coordinate system instead of image transformation. It lets you see your image without distortions caused by transformation.

Another feature is user defined grid. AerialWare lets you set custom delimiters, so you can get either whatever you want or some standard grid depending on entered values.

# Working with a program:
Everything is written in the program, no need to read other resources. Process is divided into 4 steps and shouldn't take a lot of time. Follow instructions and click "Next" to go to the next step.

# Installation
There is no installer yet, so please follow instructions below. *Unless there is some crazy guy that maintains this stuff for your distro XD*
1. Install these dependencies:
   * Python 3
   * PyQt5
2. Download the program
3. Run `python AerialWare.py`

# I wanna use it in my software!
Great! AerialWare has full fledged API and it's easy to integrate. Just follow these steps:
1. Copy AerialWare to directory inside your app and import it:
    `import AerialWare.py`
2. Create instance of this class and call getQWidget():
    `self.program = AerialWare().getQWidget()`
3. Put it somewhere in your app.
4. When user is done AerialWare will emit corresponding signal. Connect 'done' signal to your slot:
    `self.program.done.connect(self.slot)`
5. Get results. In your slot call any method of the program as you want:
    ```
    def slot(self):
      # Process results
      # ...
    ```
6. Close the program. It is your responsibility to do this. You may want to leave the program and re-process results so user will not go through the whole stuff again.

You can find the documentation [here]https://github.com/matafokka/AerialWare/wiki/AerialWare-API

# I wanna translate AerialWare!
Awesome! Just follow these steps:
1. Navigate to *lang* directory. All locales are here.
2. Copy any default language and use it as an example and reference.
3. Check comments in file for some guidlines and tips.
5. Translate and make a pool request!
