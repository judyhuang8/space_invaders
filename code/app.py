"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There
is no need for any additional classes in this module.  If you need more classes, 99% of
the time they belong in either the wave module or the models module. If you are unsure
about where a new class should go, post a question on Piazza.

Catherine Li cwl83, Judy Huang jh994
December 4, 2018
"""
from consts import *
from game2d import *
from wave import *


# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py

class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application

    This class extends GameApp and implements the various methods necessary for processing
    the player inputs and starting/running a game.

        Method start begins the application.

        Method update either changes the state or updates the Play object

        Method draw displays the Play object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.

    The primary purpose of this class is to manage the game state: which is when the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.

    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_DEATH,
                STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]
        _text:  the currently active message
                [GLabel, or None if there is no message to display]

    STATE SPECIFIC INVARIANTS:
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.

    For a complete description of how the states work, see the specification for the
    method update.

    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be
    documented here.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _lastkeys:      if the input key in the previous animation frame was held down [bool]
        _oldlives:      the number of lives after previous waves [int]
        _oldscore:      the score after previous waves [int]
        _oldalienspeed: the alien speed after the previous waves [int or float]
        _laterwave:     if the current wave is not the first [bool]
    """

    # DO NOT MAKE A NEW INITIALIZER!

    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.

        This method is distinct from the built-in initializer __init__ (which you
        should not override or change). This method is called once the game is running.
        You should use it to initialize any game specific attributes.

        This method should make sure that all of the attributes satisfy the given
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message
        (in attribute _text) saying that the user should press to play a game.
        """
        self._lastkeys = False
        self._state = STATE_INACTIVE
        self._oldlives = 3
        self._oldscore = 0
        self._laterwave = False

        self._welcomeText()

    def update(self,dt):
        """
        Animates a single frame in the game.

        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.

        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_DEATH, STATE_PAUSED, and STATE_COMPLETE.  Each one of these
        does its own thing and might even needs its own helper.  We describe these below.

        STATE_INACTIVE: This is the state when the application first opens.  It is a
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).

        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.

        STATE_DEATH: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen. This occurs after a life is lost.

        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.

        STATE_COMPLETE: The wave is over, and is either won or lost.

        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        assert type(dt) == int or float

        if self._state == STATE_INACTIVE:
            self._determineState()
        elif self._state == STATE_NEWWAVE:
            self._text = None
            self._wave = Wave()
            self.afterFirst()
            self._state = STATE_ACTIVE
        elif (self._state == STATE_ACTIVE and self._wave.getShip() != None and
            self._wave.getNoAliens() == False and self._wave.dLineCollision() != True):
            self._wave.update(self.input,dt)
            self._determinePause()
        elif self._state==STATE_PAUSED:
            self._pauseText()
            self._determineState()
        elif (self._wave.getShip() == None and self._wave.getLives() != 0):
            self._state = STATE_DEATH
            self._deathText()
            self._determineState()
        elif ((self._wave.getShip() == None and self._wave.getLives() == 0)
                or self._wave.dLineCollision() == True):
            self._state = STATE_COMPLETE
            self._gameOverText()
        elif self._wave.getNoAliens() != False:
            self._state = STATE_COMPLETE
            self._completeText()
            self._determineState()

    def afterFirst(self):
        """
        Sets new wave's lives, score, and alien speed appropriately based on
        the previous wave.

        This only occurs if it is not the first wave (self._laterwave == True).
        """
        if self._laterwave == True:
            self._wave.setLives(self._oldlives)
            self._wave.setScore(self._oldscore)
            self._wave.setAlienSpeed(self._oldalienspeed*(1/0.97)**
                    (3*ALIEN_ROWS*ALIENS_IN_ROW/4))

    def draw(self):
        """
        Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.  To draw a GObject
        g, simply use the method g.draw(self.view).  It is that easy!

        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in
        Wave. In order to draw them, you either need to add getters for these attributes
        or you need to add a draw method to class Wave.  We suggest the latter.  See
        the example subcontroller.py from class.
        """
        if self._text != None:
            try:
                self._wave.draw(self.view)
                if isinstance(self._text,list):
                    for x in self._text:
                        x.draw(self.view)
                else:
                    self._text.draw(self.view)
            except AttributeError:
                if isinstance(self._text,list):
                    for x in self._text:
                        x.draw(self.view)
                else:
                    self._text.draw(self.view)
        else:
            self._wave.draw(self.view)

    def _determineState(self):
        """
        Determines the current state and assigns it to self.state

        This method checks for a key press, and if there is one, changes the state
        to the next value.  A key press is when a key is pressed for the FIRST TIME.
        We do not want the state to continue to change as we hold down the key.  The
        user must release the key and press it again to change the state.
        """
        # Determine the current number of keys pressed
        curr_keys = self.input.is_key_down('s')

        change = curr_keys == True and self._lastkeys == False

        if change:
            if self._state == STATE_INACTIVE:
                self._state = STATE_NEWWAVE
            elif self._state == STATE_DEATH or self._state == STATE_PAUSED:
                self._state = STATE_ACTIVE
                self._text = None
                self._wave.makeShip()
            elif self._state == STATE_COMPLETE:
                self._oldlives = self._wave.getLives()
                self._oldscore = self._wave.getScore()
                self._oldalienspeed = self._wave.getAlienSpeed()
                self._laterwave = True
                self._state = STATE_NEWWAVE

        self._lastkeys = curr_keys

    def _determinePause(self):
        """
        Determines if the game is paused assign STATE_PAUSED to self._state

        This method checks if the 'escape' key is pressed, and if there is one,
        changes the state to the next value.  A key press is when a key is
        pressed for the FIRST TIME. We do not want the state to continue to
        change as we hold down the key. The user must release the key and press
        it again to change the state.
        """
        # Determine the current number of keys pressed
        curr_keys = self.input.is_key_down('escape')
        change = curr_keys == True and self._lastkeys == False
        if change and self._state == STATE_ACTIVE:
            self._state = STATE_PAUSED
        self._lastkeys = curr_keys

    def _pauseText(self):
        """
        Creates the message when the player dies.
        """
        self._text = GLabel(text="GAME PAUSED\nLives Remaining: "
                            + str(self._wave.getLives())
                            + "\n\nPress 'S' to Continue",
                            font_name='Arcade.ttf',
                            font_size=50,halign='center',valign='middle',
                            linecolor='yellow', fillcolor=[0,0,0,0.5],
                            width=GAME_WIDTH, height=GAME_HEIGHT,
                            x=GAME_WIDTH/2,y=GAME_HEIGHT/2)

    def _deathText(self):
        """
        Creates the message when the player dies.
        """
        self._text = GLabel(text="YOU DIED\nLives Remaining: "
                            + str(self._wave.getLives())
                            + "\n\nPress 'S' to Continue",
                            font_name='Arcade.ttf',
                            font_size=50,halign='center',valign='middle',
                            linecolor='yellow', fillcolor=[0,0,0,0.5],
                            width=GAME_WIDTH, height=GAME_HEIGHT,
                            x=GAME_WIDTH/2,y=GAME_HEIGHT/2)

    def _gameOverText(self):
        """
        Creates the message when the game is over.
        """
        self._text = GLabel(text="GAME OVER",font_name='Arcade.ttf',
                            font_size=80,halign='center',valign='middle',
                            linecolor='red',fillcolor=[0,0,0,0.8],
                            width=GAME_WIDTH, height=GAME_HEIGHT,
                            x=GAME_WIDTH/2,y=GAME_HEIGHT/2)

    def _completeText(self):
        """
        Creates the message when the wave is complete.
        """
        self._text = GLabel(text="WAVE COMPLETE\n\nPress 'S' to\nStart a New Wave",
                            font_name='Arcade.ttf',font_size=80,halign='center',
                            valign='middle',linecolor='yellow',fillcolor=[0,0,0,0.8],
                            width=GAME_WIDTH, height=GAME_HEIGHT,
                            x=GAME_WIDTH/2,y=GAME_HEIGHT/2)

    def _welcomeText(self):
        """
        Creates the welcome message.
        """
        if self._state == STATE_INACTIVE:
            self._text = [GLabel(text="Welcome to \nSpace Invaders",
                        font_name='Arcade.ttf',font_size=100,halign='center',
                        valign='middle',linecolor='yellow', height=GAME_HEIGHT+400,
                        width=GAME_WIDTH,x=GAME_WIDTH/2,y=GAME_HEIGHT-150,
                        fillcolor='black'),
                        GLabel(text="INSTRUCTIONS:"
                        + "\nUse the left and right arrow keys to move,"
                        + "\nand the spacebar to shoot at the aliens. "
                        + "\nThe goal is kill all the aliens in each wave,"
                        + "\nand the following waves are harder than the last."
                        + "\nPress 'M' to toggle mute and 'escape' to pause. "
                        + "\nYour lives are displayed in the upper right corner.",
                        font_name='Arcade.ttf',font_size=30,halign='center',
                        valign='middle',linecolor=[1,1,0,0.8],
                        x=GAME_WIDTH/2,y=300),
                        GLabel(text="Press 'S' to Play",font_name='Arcade.ttf',
                        font_size=50,halign='center',valign='middle',x=GAME_WIDTH/2,
                        y=100,linecolor='yellow')]
        else:
            self._text = None
