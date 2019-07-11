# AerialWare
AerialWare calculates and draws paths for aerial photography

# About AerialWare
AerialWare calculates and draws paths for aerial photography.

Main feature of AerialWare is transformation of coordinate system instead of image transformation. It lets you see your image without distortions caused by transformation.

# Working with a program:
Everything is written in the program, no need to read other resources. Proccess is divided into 3 steps and shouldn't take a lot of time. Follow instructions and click "Next" to go to the next step.

# Installation
There is no installer yet, so please follow instructions below. *Unless there is some crazy guy that maintains this stuff for your distro XD*
1. Install these dependencies:
   * Python 3
   * PyQt5
2. Download the program
3. Run `python AerialWare.py`

# I wanna use it in my software!
Great! AerialWare is easy to integrate, just follow these steps:
1. Copy AerialWare to directory inside your app.
    `Include AerialWare.py`
2. Create instance of this class and call getQWidget():
    `self.program = AerialWare().getQWidget()`
3. Put it somewhere in your app.
4. When user is done AerialWare will emit corresponding signal. Connect 'done' signal to your slot:
    `self.program.done.connect(self.slot)`
5. Get results. In your slot call getResults() method of the program:
    ```
    def slot(self):
      results = self.program.getResults()
      # Process results
      ...
    ```
6. Close the program. It is your responsibility to do this. You may want to leave the program and re-process results so user will not go through the whole stuff again.

# I wanna translate AerialWare!
Nice! Just follow these steps:
1. Navigate to *lang* directory. All languages are here.
2. Copy any default language and use it as an example and reference.
3. There are no info where specific line is used. But this hints can help you:
    * *name* variable in the beginning -- name of the language
    * Everything is written as it goes in UI or code (in getSpecial() function), so you can use the program to understand what is going on.
    * Change only text, don't touch anything else. AerialWare uses unified interface for languages, but doesn't check if files are invalid. And same positions will help other translators.
4. Check everything because wrong translation will crash the program.
5. Make a pool request!
