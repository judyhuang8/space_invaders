"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Catherine Li cwl83, Judy Huang jh994
December 4, 2018
"""
from game2d import *
from consts import *
from models import *
import random
import math

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _bground:       the background of the game [GRectangle]
        _direction:     the direction of the aliens [either 'right' or 'left']
        _alienStep:     the x-value change of the aliens since the last "step" [number >= 0]
        _randBoltRate:  the # of Alien steps determining bolt rate
                        [1 <= random int <= BOLT_RATE]
        _bgTime:        the amount of time since the last bground "step" [num >= 0]
        _alienBoltTime: the amount of time since the last alien bolt "step" [num >= 0]
        _alienSpeed:    the number of seconds between alien steps [0 < float <= 1]
        _alienFrCount:  the number of frames passed [int >= 0]

        _shipPew:       the sound made when the ship shoots [Sound]
        _alienPew:      the sound made when an alien shoots [Sound]
        _shipBlast:     the sound made when the ship is shot [Sound]
        _alienPop:      the sound made when an alien is shot [Sound]
        _musicNote:     the current note being played [Sound]
        _musicSounds:   the list of notes [list of Sounds]
        _musicNotePos:  the position of the note in the list [0 =< 0 int <= 3]
        _mute:          whether the sound is muted or not [bool, True or False]
        _muteIcon:      the icon on the screen that displays mute on/off [GImage]

        _lastkeys:      if the input key in the previous animation frame was held down [bool]


        _noAliens:      whether all aliens have been shot [bool, True or False]

        _scoreValue:    the score value, increases by 100 as an alien is killed [int]
        _scoreWord:     the display of the word "score" [GLabel]
        _score:         the display of scoreValue [GLabel]

        _lifeIcons      the display of life counter [a list of GImages]

    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getShip(self):
        """
        Returns: the ship Object.
        """
        return self._ship

    def getAliens(self):
        """
        Returns: the 2d list of aliens in the wave.
        """
        return self._aliens

    def getLives(self):
        """
        Returns: the number lives.
        """
        return self._lives

    def getNoAliens(self):
        """
        Returns: the value of _noAliens.
        """
        return self._noAliens

    def getScore(self):
        """
        Returns: the value of the score.
        """
        return self._scoreValue

    def getAlienSpeed(self):
        """
        Returns: the number of seconds between alien steps.
        """
        return self._alienSpeed

    def setLives(self,lives):
        """
        Sets the lives to the given value.

        Parameter value: the new # of lives
        Precondition: value is an int.
        """
        self._lives = lives

    def setScore(self,score):
        """
        Sets the score value to the given value.

        Parameter value: the new score
        Precondition: value is an int.
        """
        self._scoreValue = score

    def setAlienSpeed(self,speed):
        """
        Sets the alien's speed to the given value.

        Parameter value: the new alien speed
        Precondition: value is a number (int or float).
        """
        self._alienSpeed = speed

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializes the wave subcontroller.
        """
        # DRAW RELATED ATTRIBUTES
        self.makeBground()
        self.makeWave()
        self.makeShip()
        self.makeLine()
        self.makeMuteIcon()
        self._bolts = []

        # TIME RELATED ATTRIBUTES (ANIMATIONS, BOLT CREATION, ETC.)
        self.timeInit()

        # LIVES
        self._lives = 3
        self.makeLives()

        # SOUND RELATED ATTRIBUTES
        self.soundInit()

        # IF ALIENS ALL DEAD
        self._noAliens = False

        # SCORE
        self._scoreValue = 0
        self.makeScoreAndScoreWord()

    # HELPER METHODS FOR INIT (ALIENS, SHIP, GRAPHICS, SOUNDS)
    def makeWave(self):
        """
        Initializes the wave of aliens.

        Creates a 2D list of Alien objects for the current wave.
        """
        self._aliens = []
        for k in range(ALIEN_ROWS):
            self._aliens.append([])
            for j in range(ALIENS_IN_ROW):
                self._aliens[k].append(Alien(x=(j+1)*ALIEN_H_SEP+(2*j+1)*0.5*ALIEN_WIDTH,
                                            y=(GAME_HEIGHT-ALIEN_CEILING-(ALIEN_ROWS-1)*
                                            ALIEN_V_SEP-(2*ALIEN_HEIGHT*ALIEN_ROWS-1)/2)
                                            +k*ALIEN_V_SEP+(2*k+1)*0.5*ALIEN_HEIGHT,
                                            width=ALIEN_WIDTH,
                                            height=ALIEN_HEIGHT,
                                            source=ALIEN_SPRITES[(math.ceil((k+1)/2-1))%3],
                                            format=(3,2)))

    def makeAlienBolt(self):
        """
        Initializes the Alien bolts.

        Creates Bolt objects shot by random aliens in the lowest
        vertical positions at random times and adds them to self._bolts (the list
        of all bolts in the current frame).
        """
        min_aliens = self.findLowestAliens()
        if min_aliens != []:
            alien = random.choice(min_aliens)
            self._bolts.append(Bolt(x=alien.getX(),y=alien.getY(),
                                 height=BOLT_HEIGHT,width=BOLT_WIDTH,fillcolor='yellow',
                                 linecolor='white',velocity=-ALIEN_BOLT_SPEED))
            if self._alienPew != None:
                self._alienPew.play()
        self._randBoltRate = random.randint(1,BOLT_RATE)
        self._alienBoltTime = 0

    def findLowestAliens(self):
        """
        Returns a list of the Alien objects (not NoneType) at the lowest vertical
        positions in each column of _aliens.
        """
        temp_column = []
        min_aliens = []
        for i in range(ALIENS_IN_ROW):
            for j in range(ALIEN_ROWS):
                if self._aliens[j][i] != None:
                    temp_column.append(self._aliens[j][i])
            if temp_column != []:
                min_aliens.append(temp_column[0])
                temp_column = []
        return min_aliens

    def makeShip(self):
        """
        Initializes the player's ship.
        """
        self._ship = Ship(x=GAME_WIDTH/2,y=SHIP_BOTTOM,width=SHIP_WIDTH,
                            height=SHIP_HEIGHT,source='ship.png')

    def makeShipBolt(self,input):
        """
        Initializes the player's bolts.

        Creates Bolt objects shot by the player by pressing 'spacebar'
        and adds them to self._bolts (the list of all bolts in the current frame).

        Plays a sound when the bolt is shot and created.

        Parameter input:    the user input used to make a player bolt
        Precondition:       it is an instance of GInput; inherited from GameApp
        """
        num_player_bolts = 0
        if input.is_key_down('spacebar'):
            for bolt in self._bolts:
                if bolt.getIsPlayerBolt():
                    num_player_bolts += 1
            if num_player_bolts == 0 and self._ship != None:
                self._bolts.append(Bolt(x=self._ship.getX(),y=self._ship.getY(),
                                    height=BOLT_HEIGHT,width=BOLT_WIDTH,fillcolor='yellow',
                                    linecolor='white',velocity=PLAYER_BOLT_SPEED))
                if self._shipPew != None:
                    self._shipPew.play()


    def makeLine(self):
        """
        Initializes the defense line.
        """
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
                            linewidth=1,linecolor='white')

    def makeMuteIcon(self):
        """
        Initializes the mute icon.
        """
        self._muteIcon = GImage(x=GAME_WIDTH - 40,y=GAME_HEIGHT - 40,width=40,
                                height=40,source='soundOn.png')

    def makeScoreAndScoreWord(self):
        """
        Initializes the score label and the score.
        """
        self._scoreWord = GLabel(text="Score: ",font_name='Arcade.ttf',
                font_size=50,halign='center',valign='middle',linecolor='yellow',
                x=100,y=GAME_HEIGHT-50)
        self._score = GLabel(text=str(self._scoreValue),
                            font_name='Arcade.ttf',
                            font_size=50,halign='left',valign='middle',
                            linecolor='white',
                            x=250,y=GAME_HEIGHT-50)

    def makeLives(self):
        """
        Initializes the life icons.
        """
        self._lifeIcons = []
        for x in range(self._lives):
            self._lifeIcons.append(GImage(x=GAME_WIDTH - 100 - 40*x,
                                            y=GAME_HEIGHT-40,width=35,
                                            height=35,source='ship.png'))

    def makeBground(self):
        """
        Initializes the background.
        """
        self._bground = GSprite(x=GAME_WIDTH/2,y=GAME_HEIGHT/2,width=800,
                                height=700,source='linearsprite2.png',format=(1,8))

    def timeInit(self):
        """
        Initializes the time-related attributes.
        """
        self._time = 0
        self._randBoltRate = random.randint(1,BOLT_RATE)
        self._bgTime = 0
        self._alienBoltTime = 0
        self._direction = 'right'
        self._alienSpeed = ALIEN_SPEED
        self._alienFrCount = 0

    def soundInit(self):
        """
        Initializes the sound-related attributes.
        """
        self._shipPew = Sound('pew1.wav')
        self._alienPew = Sound('pew2.wav')
        self._shipBlast = Sound(random.choice(['blast1.wav','blast2.wav','blast3.wav']))
        self._alienPop = Sound(random.choice(['pop1.wav','pop2.wav']))
        self._musicSounds = [Sound('musicNote1.wav'),Sound('musicNote2.wav'),
                                Sound('musicNote1.wav'),Sound('musicNote3.wav')]
        self._musicNotePos = 0
        self._musicNote = self._musicSounds[self._musicNotePos]

        self._mute = False

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,input,dt):
        """
        Animates a single animation frame in the wave.

        Parameter input:    the user input used to make a player bolt
        Precondition:       it is an instance of GInput; inherited from GameApp

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        if self._ship != None:
            self._ship.moveShip(input)
            self.makeShipBolt(input)
        self.moveShipBolts()
        self.moveAlienBolts()
        self.isEachPlayerBolt()
        if self._time >= self._alienSpeed:
            self.moveAliensH()
            if self._musicSounds != None:
                self._musicNote.play()
                self._musicNotePos = (self._musicNotePos + 1)%4
        if self._alienBoltTime >= self._randBoltRate * self._alienSpeed:
            self.makeAlienBolt()
        if self._bgTime >= BACKGROUND_SPEED:
            self.animateBground()
        else:
            self._time = self._time + dt
            self._bgTime = self._bgTime + dt
            self._alienBoltTime += dt
        self.alienCollision()
        self.dLineCollision()
        self.shipCollision()
        self.noAliens()
        self.makeLives()
        self.mute(input)
        self.unmute(input)
        self.updateScore()
        self.updateMusicNote()

    # UPDATE METHOD HELPERS
    def moveAliensH(self):
        """
        Moves the wave of aliens horizontally until they reach one separation from
        the edge of the screen, and then moves them down one separation.

        The method first records all the x-coordinates of the alive Aliens in the wave;
        then it finds the maximum and minimum x-coordinates to determine the edges
        of the wave. It checks the direction of motion and if the boundary of the wave
        has reached that direction's side of the playing field; if the latter is true,
        it calls the helper function for vertical motion and moves the aliens down.
        Then it reverses the direction.

        Otherwise, it moves the wave horizontally based on a predetermined speed.
        Also, the horizontal motion occurs in steps after each certain number of
        animation frames determined by the _alienSpeed attribute, so it resets the
        time counter (which measures animation frames passed) to 0.
        """
        alien_positions = []
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien_positions.append(alien.getX())
        if alien_positions != []:
            rightmost = max(alien_positions)
            leftmost = min(alien_positions)

            if (self._direction == 'right' and rightmost >= GAME_WIDTH -
                ALIEN_H_SEP - ALIEN_WIDTH/2):
                self.moveAliensV()
                self._direction = 'left'
            elif self._direction == 'left' and leftmost <= ALIEN_H_SEP + ALIEN_WIDTH/2:
                self.moveAliensV()
                self._direction = 'right'
            else:
                for row in self._aliens:
                    for alien in row:
                        if alien != None and self._direction == 'right':
                            alien.setX(alien.getX() + ALIEN_H_WALK)
                            alien.frame = (alien.frame+1)%2
                            self._time = 0
                        if alien != None and self._direction == 'left':
                            alien.setX(alien.getX() - ALIEN_H_WALK)
                            alien.frame = (alien.frame+1)%2
                            self._time = 0

    def moveAliensV(self):
        """
        Moves the wave down when called.

        Loops over self._aliens and moves each alien down. This occurs once each
        step, so it resets the time counter to 0.
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.setY(alien.getY() - ALIEN_V_WALK)
                    alien.frame = (alien.frame+1)%2
        self._time = 0

    def moveShipBolts(self):
        """
        Moves the existing ship bolt on screen up.

        Checks if the bolt is a player bolt and increases its y-coordinate if yes;
        if the bottom of the bolt goes outside the top of the window, the bolt
        is deleted.
        """
        for bolt in self._bolts:
            if bolt.getIsPlayerBolt():
                bolt.setY(bolt.getY() + bolt.getVelocity())
                i = 0
                while i < len(self._bolts):
                    if self._bolts[i].getY() > GAME_HEIGHT + BOLT_HEIGHT/2:
                        del self._bolts[i]
                    else:
                        i += 1

    def moveAlienBolts(self):
        """
        Moves the existing alien bolts on screen down.

        Checks if each bolt is a player bolt and decreases its y-coordinate if no;
        if the top of the bolt goes outside the bottom of the window, the bolt
        is deleted.
        """
        for bolt in self._bolts:
            if not bolt.getIsPlayerBolt():
                bolt.setY(bolt.getY() + bolt.getVelocity())
                i = 0
                while i < len(self._bolts):
                    if self._bolts[i].getY() < 0 - BOLT_HEIGHT/2:
                        del self._bolts[i]
                    else:
                        i += 1

    def animateBground(self):
        """
        Animates the background GSprite.

        Increments the frame attribute of the GSprite and resets background-specific
        time steps to 0.
        """
        self._bground.frame = (self._bground.frame+1)%8
        self._bgTime = 0

    def isEachPlayerBolt(self):
        """
        Checks if each bolt is a player bolt.

        Loops through the bolts to check, mainly to update the values of isPlayerBolt
        for each bolt every animation frame.
        """
        for bolt in self._bolts:
            bolt.isPlayerBolt()

    def updateScore(self):
        """
        Updates the display of score to be _scoreValue.

        Used to update the display of score every animation frame without creating
        a new GLabel object each time.
        """
        self._score.text = str(self._scoreValue)

    def updateMusicNote(self):
        """
        Updates the current playing music note to be an element of _musicSounds.

        Used to update the current music note to loop through the _musicSounds
        list; it is checked every animation frame, but only changes every alien
        step.
        """
        if self._musicSounds != None:
            self._musicNote = self._musicSounds[self._musicNotePos]

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self,view):
        """
        Draws the game objects in wave to the view.

        This method draws all of the objects in wave. If there is sound, it
        will draw the unmuted sound icon. If there is no sound, it will draw the
        muted sound icon.

        This method also loops through all of the aliens and
        bolts in _aliens and _bolts, respectively, and draws those.

        If the ship attribute is not None, it will draw the ship.

        If there are still lives remaining, it will draw the number of ships
        remaining on the top right corner of the screen

        It will always draw the defense line and the score.
        """
        self._bground.draw(view)
        self._muteIcon.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        for life in self._lifeIcons:
            life.draw(view)
        self._dline.draw(view)
        self._scoreWord.draw(view)
        self._score.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
    def alienCollision(self):
        """
        Sets the collided alien to none, deletes the attacking bolt, increases
        alien speed, plays a sound effect, and increases score when a player bolt
        collides with an alien.

        Loops through the wave and determines if any player bolt has collided with
        a currently alive alien; if this is true, it completes the above actions.
        This updates every animation frame to adjust the wave after collision.
        """
        for i in range(len(self._aliens)):
            for j in range(len(self._aliens[i])):
                for k in range(len(self._bolts)):
                    if self._aliens[i][j] != None:
                        if self._aliens[i][j].collides(self._bolts[k]):
                            self._aliens[i][j] = None
                            del self._bolts[k]
                            self._alienSpeed = self._alienSpeed*0.97
                            if self._alienPop != None:
                                self._alienPop.play()
                            self._scoreValue += 100

    def dLineCollision(self):
        """
        Returns True if the wave goes below the defense line.

        Finds the aliens with lowest y-coordinates; if the bottom of any of those
        aliens goes beneath the defense line, it returns true.
        """
        min_aliens = self.findLowestAliens()
        for alien in min_aliens:
            if alien.getY() <= DEFENSE_LINE + ALIEN_HEIGHT/2:
                return True

    def shipCollision(self):
        """
        Sets the collided ship to none, deletes the attacking bolt, decreases
        _lives by 1, plays a sound effect.

        Loops through the bolts and determines if any alien bolt has collided with
        the ship; if this is true, it completes the above actions.
        This updates every animation frame to adjust the wave after collision.
        """
        for i in range(len(self._bolts)):
            if self._ship != None:
                if self._ship.collides(self._bolts[i]):
                    self._ship = None
                    del self._bolts[i]
                    if self._shipBlast != None:
                        self._shipBlast.play()
                    self._lives -= 1

    # HELPER METHODS FOR STATE CHANGES
    def noAliens(self):
        """
        Checks if there are no aliens left.

        Loops through the wave to see if all aliens are type None; if this is
        true, it sets the attribute _noAliens to true.
        """
        num_aliens = 0
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    num_aliens += 1
        if num_aliens == 0:
            self._noAliens = True

    # HELPER METHODS FOR MUTING
    def mute(self,input):
        """
        Mutes all of the sounds in the game.

        This method checks if _nosound == False (there is sound), then once the
        player presses the key 'm', all of the sound objects in the game is set
        to None. A key press is when a key is pressed for the FIRST TIME. We do
        not want the sound to continue to change as we hold down the key. After
        setting all of the sounds to None, the sound icon is also changed to an
        image where there is no sound.
        """
        if self._mute == False:
            curr_keys = input.is_key_down('m')
            change = curr_keys == True and self._lastkeys == False

            if change:
                self._shipPew = None
                self._alienPew = None
                self._shipBlast = None
                self._alienPop = None
                self._musicSounds = None
                self._mute = True
                self._muteIcon = GImage(x=GAME_WIDTH - 40,y=GAME_HEIGHT - 40,width=40,
                                        height=40,source='soundOff.png')
            self._lastkeys = curr_keys

    def unmute(self,input):
        """
        Unmutes all of the sounds in the game.

        This method checks if _nosound == True (there is no sound), then once the
        player presses the key 'm', all of the sound objects in the game is reset
        to its original sound objects. A key press is when a key is pressed for
        the FIRST TIME. We do not want the sound to continue to change as we hold
        down the key. After setting all of the sounds to back to the original
        sound objects, the sound icon is also changed to an image where there is sound.
        """

        if self._mute == True:
            curr_keys = input.is_key_down('m')
            change = curr_keys == True and self._lastkeys == False

            if change:
                self._shipPew = Sound('pew1.wav')
                self._alienPew = Sound('pew2.wav')
                self._shipBlast = Sound(random.choice(['blast1.wav','blast2.wav','blast3.wav']))
                self._alienPop = Sound(random.choice(['pop1.wav','pop2.wav']))
                self._musicSounds = [Sound('musicNote1.wav'),Sound('musicNote2.wav'),
                                        Sound('musicNote1.wav'),Sound('musicNote3.wav')]
                self._mute = False
                self._muteIcon = GImage(x=GAME_WIDTH - 40,y=GAME_HEIGHT - 40,width=40,
                                        height=40,source='soundOn.png')

            self._lastkeys = curr_keys
