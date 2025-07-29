from cmu_graphics import *
import math
import time
import random
try:
    import kaomoji
    KAOMOJI_AVAILABLE = True
except ImportError:
    KAOMOJI_AVAILABLE = False

# complex Unicode kaomoji (ideal)
# taken from emojicombos.com/kaomoji
HAPPY_KAOMOJI = "(=^·ω·^=)"
SAD_KAOMOJI = "( ˘︹˘ )"
NEUTRAL_KAOMOJI = "(•-•)"
EATING_KAOMOJI = "(*˘ڡ˘*)"
EXCITED_KAOMOJI = "\(^Д^)/"
SLEEPING_KAOMOJI = "(˘o˘) z z Z"
SPARKLES_KAOMOJI = "*,+.~"

# fallback ASCII kaomoji if Unicode doesn't work
# from emojicombos.com/kaomoji (and my own custom kaomoji that i made)
HAPPY_KAOMOJI_SIMPLE = "(^_^)"
SAD_KAOMOJI_SIMPLE = "(-_-)"
NEUTRAL_KAOMOJI_SIMPLE = "(o_o)"
EATING_KAOMOJI_SIMPLE = "(nom)"
EXCITED_KAOMOJI_SIMPLE = "\\o/"
SLEEPING_KAOMOJI_SIMPLE = "(zzz)"
SPARKLES_KAOMOJI_SIMPLE = "(*)"

# font options to try for better Unicode support
UNICODE_FONTS = ['arial', 'helvetica', 'times', 'courier', 'verdana']
DEFAULT_FONT = 'monospace'

class FurniturePiece:
    def __init__(self, name, x, y, width, height, variants):
        self.name = name
        self.x = x  # top-left corner
        self.y = y  # top-left corner
        self.width = width
        self.height = height
        self.variants = variants  # list of PNG filenames
        self.currentVariant = 0  # index of current variant (0 = original/none)
        
    def isClicked(self, mouseX, mouseY):
        return (self.x <= mouseX <= self.x + self.width and 
                self.y <= mouseY <= self.y + self.height)
    
    def cycleVariant(self):
        self.currentVariant = (self.currentVariant + 1) % len(self.variants)
        
    def getCurrentVariantPath(self):
        if self.currentVariant == 0:
            return None  # no overlay, use original background (pre-drawn furniture)
        return f"images/furniture/{self.variants[self.currentVariant]}"

class Cat:
    def __init__(self, name, x, y, personality=None):
        self.name = name
        self.x = x
        self.y = y
        
        # store last valid position for placement restrictions
        self.lastValidX = x
        self.lastValidY = y
        
        # tamagotchi-style stats (0-100)
        self.hunger = 50
        self.happiness = 50
        self.energy = 50
        self.cleanliness = 50
        
        # animation and behavior
        self.mood = "neutral"
        self.animationFrame = 0
        self.lastActionTime = 0
        self.isSleeping = False
        self.activity = "idle"
        
        # player interaction
        self.beingPetted = False
        self.customerSatisfaction = 0
        
        # dragging state
        self.isBeingDragged = False
        self.dragOffsetX = 0
        self.dragOffsetY = 0
        
        self.currentFrame = 0
        self.animationSpeed = 12 
        self.frameTimer = 0
        
        self.spriteFrames = {
            "idle_neutral": 6,    # all cats have ~6 frames for idle neutral
            "idle_happy": 8,      # all cats have ~8 frames for idle happy
            "idle_sad": 6,        # all cats have ~6 frames for idle sad
            "sleeping": 2,        # all cats have ~2 frames for sleeping
            "dangling": 1,        # 2 frames for dangling (frames of jumping of happy)
            "running": 7,         # 7 frames for running animation
        }
        
        # personality 
        self.personality = personality or {
            'hungerRate': 1.0,
            'energyRate': 1.0,
            'messyRate': 1.0,
            'socialNeed': 1.0,
            'playfulness': 1.0,
            'sleepiness': 1.0
        }

        self.isSelected = False
        
        # running behavior
        self.isRunning = False
        self.runTimer = 0
        self.runDuration = 0
        self.runTargetX = 0
        self.runTargetY = 0
        self.runSpeed = 1.2
        self.facingLeft = False

    def feed(self):
        self.hunger = min(100, self.hunger + 15)
        self.happiness = min(100, self.happiness + 5)
        self.activity = "eating"
        
    def play(self):
        if self.energy > 20:
            self.happiness = min(100, self.happiness + 12 * self.personality['playfulness'])
            self.energy = max(0, self.energy - 8)
            self.activity = "playing"
        
    def clean(self):
        self.cleanliness = min(100, self.cleanliness + 20)
        self.happiness = min(100, self.happiness + 3)
        self.activity = "cleaning"

    def startDrag(self, mouseX, mouseY):
        self.isBeingDragged = True
        self.dragOffsetX = mouseX - self.x
        self.dragOffsetY = mouseY - self.y
        self.happiness = max(0, self.happiness - 1)

    def updateDragPosition(self, mouseX, mouseY):
        if self.isBeingDragged:
            self.x = mouseX - self.dragOffsetX
            self.y = mouseY - self.dragOffsetY

    def updateRunning(self):
        # we need to handle "random" running
        if not self.isBeingDragged and not self.isSleeping and not self.isRunning:
            # only start running if cat is not sleeping and not already running
            # much lower chance 
            chance = random.randint(1, 1000) 
            threshold = 3 * self.personality['playfulness']
            if chance < threshold:
                self.startRunning()
        
        # if currently running
        if self.isRunning:
            self.runTimer += 1
            
            # move towards target
            dx = self.runTargetX - self.x
            dy = self.runTargetY - self.y
            distance = (dx**2 + dy**2)**0.5
            
            # always face right when running
            self.facingLeft = False
            
            if distance > 2: 
                # an attempt tp make a smooth movement towards the target
                moveX = (dx / distance) * self.runSpeed
                moveY = (dy / distance) * self.runSpeed
                
                # stronger easing when close to target for smoother approach
                if distance < 80:
                    easeFactor = distance / 80
                    moveX *= easeFactor * 0.7  # extra smoothing factor
                    moveY *= easeFactor * 0.7
                
                self.x += moveX
                self.y += moveY
            else:
                self.stopRunning()
            
            # stop running after duration
            if self.runTimer > self.runDuration:
                self.stopRunning()

    def startRunning(self):
        self.isRunning = True
        self.runTimer = 0
        self.runDuration = random.randint(90, 150)  # run for 3-5 seconds (30 fps = 90-150 frames)
        
        # pick a random valid target position that's to the RIGHT of current position
        attempts = 0
        while attempts < 10:  # try to find valid position
            minX = max(80, int(self.x + 50))
            maxX = 1200
            if minX < maxX:
                targetX = random.randint(max(100, int(self.x + 50)), 1800)  # only targets to the right
                targetY = random.randint(100, 900)
                if isValidPosition(targetX, targetY):
                    self.runTargetX = targetX
                    self.runTargetY = targetY
                    break
                attempts += 1
        
        # if no valid position found to the right, pick any valid position
        if attempts >= 10:
            attempts = 0
            while attempts < 10:
                targetX = random.randint(100, 1800)
                targetY = random.randint(100, 900)
                if isValidPosition(targetX, targetY):
                    self.runTargetX = targetX
                    self.runTargetY = targetY
                    break
                attempts += 1
        
        # boost happiness slightly when running
        if self.personality['playfulness'] > 1.0:
            self.happiness = min(100, self.happiness + 2)
        
        self.activity = "running"

    def stopRunning(self):
        self.isRunning = False
        self.runTimer = 0
        self.activity = "idle"

    def stopDrag(self):
        # when stopping drag, check if position is valid:
        if isValidPosition(self.x, self.y):
            # accept new position
            self.lastValidX = self.x
            self.lastValidY = self.y
        else:
            # revert to last valid position
            self.x = self.lastValidX
            self.y = self.lastValidY
        
        self.isBeingDragged = False
        self.happiness = min(100, self.happiness + 2)

    def getCurrentAnimationState(self):
        # check if being dragged first - use dangling animation
        if self.isBeingDragged:
            return "dangling"
        # check if running (this should come BEFORE sleeping check)
        elif self.isRunning:
            return "running"
        # check if sleeping (only if not running)
        elif self.isSleeping and not self.isRunning:
            return "sleeping"
        # otherwise use idle animations based on mood
        elif self.mood == "happy":
            return "idle_happy"
        elif self.mood == "sad":
            return "idle_sad"
        else:
            return "idle_neutral"

    def updateAnimation(self):
        self.frameTimer += 1
        
        # different animation speeds for different states
        currentState = self.getCurrentAnimationState()
        if currentState == "dangling":
            animationSpeed = 15  # moderate speed for dangling animation
        elif currentState == "running":
            animationSpeed = 5  # faster running 
        elif currentState == "sleeping":
            animationSpeed = 20  # slower for peaceful sleeping
        elif currentState == "idle_happy":
            animationSpeed = 8   # faster for happy/energetic cats
        else:
            animationSpeed = self.animationSpeed  # normal-ish speed for neutral/sad
            
        if self.frameTimer >= animationSpeed:
            self.frameTimer = 0
            
            # get current animation state and frame count
            maxFrames = self.spriteFrames.get(currentState, 1)
            
            # cycle through frames
            self.currentFrame = (self.currentFrame + 1) % maxFrames

    def getSpritePath(self):
        currentState = self.getCurrentAnimationState()
        maxFrames = self.spriteFrames.get(currentState, 1)
        
        # special handling for dangling - use happy frames 3-4 [?? have to double check number but it looks right]
        if currentState == "dangling":
            # map dangling frames 0-1 to happy frames 3-4 [??]
            actualFrame = self.currentFrame + 3
            spriteFilename = f"{self.name}_idle_happy_{actualFrame}.png"
        elif maxFrames > 1:
            # normal multi-frame animations
            frameNum = self.currentFrame  # Keep 0-indexed
            spriteFilename = f"{self.name}_{currentState}_{frameNum}.png"
        else:
            # single frame animations
            spriteFilename = f"{self.name}_{currentState}.png"
            
        return f"images/cats/{spriteFilename}"

    def updateStats(self, timeMultiplier=1):
        self.hunger = max(0, self.hunger - (0.1 * self.personality['hungerRate'] * timeMultiplier))
        self.energy = max(0, self.energy - (0.05 * self.personality['energyRate'] * timeMultiplier))
        self.cleanliness = max(0, self.cleanliness - (0.03 * self.personality['messyRate'] * timeMultiplier))

        if self.hunger < 20 or self.energy < 20 or self.cleanliness < 20:
            self.happiness = max(0, self.happiness - (0.15 * self.personality['socialNeed'] * timeMultiplier))
        elif self.hunger > 80 and self.energy > 80 and self.cleanliness > 80:
            self.happiness = min(100, self.happiness + (0.05 * timeMultiplier))

        avgStat = (self.hunger + self.happiness + self.energy + self.cleanliness) / 4
        if avgStat > 70:
            self.mood = "happy"
        elif avgStat > 40:
            self.mood = "neutral"
        else:
            self.mood = "sad"

        self.isSleeping = self.energy < 30

    def draw(self, app):
        self.animationFrame += 1
        self.updateAnimation()
        self.updateRunning()  # Add running behavior

        spriteLoaded = False

        try:
            spritePath = self.getSpritePath()
            # always draw sprites normally (facing right) since cats only run right
            drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
            spriteLoaded = True
                
        except Exception as e:
            # debug: show what file it tried to load (only for elwin for now)
            if self.name == "elwin" and not spriteLoaded:
                attemptedPath = self.getSpritePath()
                print(f"Failed to load: {attemptedPath}") 
            # fallback to old single sprite system
            try:
                if self.isSleeping:
                    spritePath = f"images/cats/{self.name}_sleeping.png"
                else:
                    spritePath = f"images/cats/{self.name}_{self.mood}.png"

                drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
                spriteLoaded = True
            except:
                # final fallback to basic cat sprite
                try:
                    spritePath = f"images/cats/{self.name}.png"
                    drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
                    spriteLoaded = True
                except:
                    pass

        # if no sprite loaded, show placeholder
        if not spriteLoaded:
            placeholderColors = {
                'churrio': rgb(255, 165, 0),
                'beepaw': rgb(128, 128, 128),
                'meeple': rgb(255, 255, 255),
                'elwin': rgb(255, 228, 196)
            }
            color = placeholderColors.get(self.name, rgb(200, 200, 200))

            drawRect(self.x - 40, self.y - 40, 80, 80, fill=color, border='black', 
                     borderWidth=2)
            drawLabel("SPRITE", self.x, self.y - 10, size=14, bold=True, font='monospace')
            drawLabel(self.name, self.x, self.y + 8, size=12, font='monospace')
            
            # show current animation state and frame for debugging
            currentState = self.getCurrentAnimationState()
            maxFrames = self.spriteFrames.get(currentState, 1)
            if maxFrames > 1:
                frameInfo = f"{currentState}_f{self.currentFrame + 1}/{maxFrames}"
            else:
                frameInfo = f"{currentState}"
            drawLabel(frameInfo, self.x, self.y + 25, 
                     size=9, font='monospace')

        if self.isBeingDragged:
            drawCircle(self.x, self.y + 5, 45, fill='black', opacity=20)

        # emotion bubble logic
        emotionPath = None

        if self.isBeingDragged:
            emotionPath = "images/emotions/surprised.png"
        elif self.hunger < 25:
            emotionPath = "images/emotions/confused.png"
        elif self.cleanliness < 25:
            emotionPath = "images/emotions/sad.png"
        elif self.energy < 20:
            emotionPath = "images/emotions/neutral.png"
        elif self.activity == "eating":
            emotionPath = "images/emotions/content.png"
        elif self.activity == "playing":
            emotionPath = "images/emotions/wow.png"
        elif self.activity == "cleaning":
            emotionPath = "images/emotions/neutral.png"
        elif self.isSleeping:
            emotionPath = "images/emotions/content.png"
        elif self.mood == "happy":
            if (self.animationFrame // 60) % 2 == 0:
                emotionPath = "images/emotions/happy.png"
            else:
                emotionPath = "images/emotions/happy2.png"
        elif self.mood == "sad":
            emotionPath = "images/emotions/sad.png"
        elif self.personality['socialNeed'] > 1.2 and self.happiness < 60:
            emotionPath = "images/emotions/meow.png"
        else:
            emotionPath = "images/emotions/neutral.png"

        bubbleX = self.x + 25
        bubbleY = self.y - 35

        if emotionPath:
            try:
                drawImage(emotionPath, bubbleX, bubbleY, align='center', width=50, height=50)
            except:
                try:
                    drawImage("images/emotions/neutral.png", bubbleX, bubbleY, align='center', width=50, height=50)
                except:
                    pass

        drawLabel(self.name, self.x, self.y + 60, size=14, bold=True, fill='cadetBlue', font='monospace')

def drawUnicodeLabel(text, x, y, size=16, bold=False, fill='black', align='center'):
    # i try to draw text with Unicode support by testing different font but it'll fall back to simple ASCII if Unicode fails
    # first try with different fonts that might support Unicode better
    for font in UNICODE_FONTS:
        try:
            drawLabel(text, x, y, size=size, bold=bold, fill=fill, align=align, font=font)
            return True
        except:
            continue
    
    # if all Unicode fonts fail, try with default font
    try:
        drawLabel(text, x, y, size=size, bold=bold, fill=fill, align=align, font=DEFAULT_FONT)
        return True
    except:
        # if even that fails, strip Unicode and use ASCII fallback
        simple_text = text.replace(HAPPY_KAOMOJI, HAPPY_KAOMOJI_SIMPLE)
        simple_text = simple_text.replace(SAD_KAOMOJI, SAD_KAOMOJI_SIMPLE)
        simple_text = simple_text.replace(NEUTRAL_KAOMOJI, NEUTRAL_KAOMOJI_SIMPLE)
        simple_text = simple_text.replace(EATING_KAOMOJI, EATING_KAOMOJI_SIMPLE)
        simple_text = simple_text.replace(EXCITED_KAOMOJI, EXCITED_KAOMOJI_SIMPLE)
        simple_text = simple_text.replace(SLEEPING_KAOMOJI, SLEEPING_KAOMOJI_SIMPLE)
        simple_text = simple_text.replace(SPARKLES_KAOMOJI, SPARKLES_KAOMOJI_SIMPLE)
        
        drawLabel(simple_text, x, y, size=size, bold=bold, fill=fill, align=align, font=DEFAULT_FONT)
        return False
    
def createCatPersonalities():
    personalities = {
        'lazy': {
            'hungerRate': 0.8, 'energyRate': 1.5, 'messyRate': 1.2,
            'socialNeed': 0.8, 'playfulness': 0.6, 'sleepiness': 1.5
        },
        'energetic': {
            'hungerRate': 1.3, 'energyRate': 0.7, 'messyRate': 1.3,
            'socialNeed': 1.2, 'playfulness': 1.8, 'sleepiness': 0.6
        },
        'clean': {
            'hungerRate': 1.0, 'energyRate': 1.0, 'messyRate': 0.5,
            'socialNeed': 1.0, 'playfulness': 1.0, 'sleepiness': 1.0
        },
        'social': {
            'hungerRate': 1.0, 'energyRate': 1.0, 'messyRate': 1.0,
            'socialNeed': 1.8, 'playfulness': 1.3, 'sleepiness': 0.8
        },
        'independent': {
            'hungerRate': 0.9, 'energyRate': 0.9, 'messyRate': 0.9,
            'socialNeed': 0.5, 'playfulness': 0.8, 'sleepiness': 1.1
        }
    }
    return personalities

def createFurniturePieces():
    # Define clickable furniture areas and their variants
    # You'll need to adjust these coordinates based on your room layout
    furniture = [
        FurniturePiece(
            name="bed",
            x=633, y=481, width=259, height=168,
            variants=["original", "bed_purple.png"]
        ),
        FurniturePiece(
            name="post",
            x=101,y=545, width=131,height=188,
            variants=["original", "post_green.png", "post_red.png"]
        ),
        # i will add more furniture pieces later
        # furniturePiece(
        #     name="bookshelf",
        #     x=100, y=200, width=60, height=150,
        #     variants=["original", "bookshelf_oak.png", "bookshelf_cherry.png"]
        # ),
    ]
    return furniture

# define allowed placement area for isometric room floor
def isValidPosition(x, y):
    # isometric room boundaries based on the floor area
    centerX = 600  
    centerY = 700      
    width = 580   
    height = 580      
    
    dx = x - centerX
    dy = y - centerY
    
    # diamond shape condition for the floor area
    return abs(dx) / (width / 2) + abs(dy) / (height / 2) <= 1

def drawFurnitureOverlays(app):
    for furniture in app.furniture:
        variantPath = furniture.getCurrentVariantPath()
        if variantPath:  # only draw if not using original
            try:
                drawImage(variantPath, furniture.x, furniture.y, 
                         width=furniture.width, height=furniture.height)
            except:
                # fallback if image doesn't exist
                drawRect(furniture.x, furniture.y, furniture.width, furniture.height,
                        fill='lightGray', border='red', borderWidth=2, opacity=50)
                drawLabel(f"Missing:\n{variantPath}", 
                         furniture.x + furniture.width//2, furniture.y + furniture.height//2,
                         size=10, fill='red', font='monospace')

# added this function to show clickable furniture areas (optional debug mode)
def drawFurnitureClickAreas(app, showDebug=False):
    if showDebug:
        for furniture in app.furniture:
            # draw clickable area outline
            drawRect(furniture.x, furniture.y, furniture.width, furniture.height,
                    fill=None, border='yellow', borderWidth=2, opacity=70)
            drawLabel(f"{furniture.name}\n{furniture.currentVariant+1}/{len(furniture.variants)}", 
                     furniture.x + furniture.width//2, furniture.y + furniture.height//2,
                     size=12, fill='yellow', font='monospace', bold=True)

def onAppStart(app):
    app.width = 1200
    app.height = 1400
    app.stepCounter = 0
    app.gameTime = 0
    app.selectedCat = None
    
    # dragging state
    app.draggingCat = None
    app.dragStartTime = 0
    app.mouseX = 0
    app.mouseY = 0
    
    # initialize paused state and sound (commented out rn)
    app.paused = False
    # app.sound = Sound(url) 

    personalities = createCatPersonalities()

    app.cats = [
        Cat("churrio", 600, 600, personalities['energetic']),
        Cat("beepaw", 400, 650, personalities['independent']),
        Cat("meeple", 800, 650, personalities['clean']),
        Cat("elwin", 1000, 700, personalities['social']),
    ]
    
    # furniture inititalize 
    app.furniture = createFurniturePieces()

    # popup menu settings
    app.popupWidth = 350
    app.popupHeight = 370
    app.popupX = 10
    app.popupY = 10
    
    # initialize actionButtons to avoid AttributeError
    app.actionButtons = {}
            
def drawStatBar(x, y, width, height, value, maxValue, color, label):
    # background bar
    drawRect(x, y, width, height, fill='lightGray', border='darkGray', borderWidth=1)
    
    # filled portion
    fillWidth = (value / maxValue) * width
    drawRect(x, y, fillWidth, height, fill=color, border=None)
    
    # text overlay
    drawLabel(f"{label}: {int(value)}", x + width//2, y + height//2, 
             size=12, bold=True, fill='darkOliveGreen' if value > 50 else 'fireBrick', font='monospace')

def updateActionButtons(app):
    if app.selectedCat:
        popupX, popupY = app.popupX, app.popupY
        popupW, popupH = app.popupWidth, app.popupHeight
        
        # calculate button positions (same logic as in drawCatPopup)
        headerHeight = 60
        statsY = popupY + headerHeight + 20
        statSpacing = 35
        activityY = statsY + statSpacing * 4 + 20
        buttonY = activityY + 60
        buttonWidth = 80
        buttonHeight = 40
        buttonSpacing = 20
        
        totalButtonWidth = buttonWidth * 3 + buttonSpacing * 2
        startX = popupX + (popupW - totalButtonWidth) // 2
        
        # close button position
        closeX = popupX + popupW - 30
        closeY = popupY + 30
        
        app.actionButtons = {
            'feed': {'x': startX, 'y': buttonY, 'w': buttonWidth, 'h': buttonHeight},
            'play': {'x': startX + buttonWidth + buttonSpacing, 'y': buttonY, 'w': buttonWidth, 'h': buttonHeight},
            'clean': {'x': startX + (buttonWidth + buttonSpacing) * 2, 'y': buttonY, 'w': buttonWidth, 'h': buttonHeight},
            'close': {'x': closeX - 15, 'y': closeY - 15, 'w': 30, 'h': 30}
        }
    else:
        app.actionButtons = {}

def drawCatPopup(app, cat):
    # popup background with rounded corners effect
    popupX, popupY = app.popupX, app.popupY
    popupW, popupH = app.popupWidth, app.popupHeight
    
    # shadow effect
    drawRect(popupX + 3, popupY + 3, popupW, popupH, fill='black', opacity=30)
    
    # main popup background
    drawRect(popupX, popupY, popupW, popupH, fill='aliceBlue', border='cadetBlue', borderWidth=3)
    
    # header section
    headerHeight = 60
    drawRect(popupX, popupY, popupW, headerHeight, fill='aliceBlue', border='cadetBlue', borderWidth=2)
    
    # cat name
    drawUnicodeLabel(f"{HAPPY_KAOMOJI} {cat.name.title()}", popupX + popupW//2, popupY + 20, 
                    size=24, bold=True, fill='cadetBlue', align='center')

    # close button (X)
    closeX = popupX + popupW - 30
    closeY = popupY + 30
    drawCircle(closeX, closeY, 15, fill='red', border='darkRed', borderWidth=2)
    drawLabel("×", closeX, closeY+1, size=20, bold=True, fill='white')

    # mood indicator 
    if cat.mood == "happy":
        moodKaomoji = HAPPY_KAOMOJI
    elif cat.mood == "sad":
        moodKaomoji = SAD_KAOMOJI
    else:
        moodKaomoji = NEUTRAL_KAOMOJI

    drawUnicodeLabel(f"Mood: {moodKaomoji} {cat.mood.title()}", popupX + popupW//2, popupY + 45, 
                    size=14, bold=True, fill='cadetBlue', align='center')
        
    # stats section
    statsY = popupY + headerHeight + 20
    statHeight = 25
    statSpacing = 35
    
    # stat bars with colors
    statColors = {
        'hunger': 'lightSalmon',
        'happiness': 'lightPink', 
        'energy': 'darkSeaGreen',
        'cleanliness': 'lightSteelBlue'
    }
    
    drawStatBar(popupX + 20, statsY, popupW - 40, statHeight, 
               cat.hunger, 100, statColors['hunger'], "Hunger")
    
    drawStatBar(popupX + 20, statsY + statSpacing, popupW - 40, statHeight,
               cat.happiness, 100, statColors['happiness'], "Happiness")
    
    drawStatBar(popupX + 20, statsY + statSpacing * 2, popupW - 40, statHeight,
               cat.energy, 100, statColors['energy'], "Energy")
    
    drawStatBar(popupX + 20, statsY + statSpacing * 3, popupW - 40, statHeight,
               cat.cleanliness, 100, statColors['cleanliness'], "Cleanliness")
    
    # activity section
    activityY = statsY + statSpacing * 4 + 20
    drawRect(popupX + 10, activityY - 10, popupW - 20, 40, fill='lightYellow', 
             border='orange', borderWidth=2)
    
    if cat.isSleeping:
        activityText = f"Current Activity: Sleeping {SLEEPING_KAOMOJI}"
    elif cat.activity == "eating":
        activityText = f"Current Activity: Eating {EATING_KAOMOJI}"
    elif cat.activity == "playing":
        activityText = f"Current Activity: Playing {EXCITED_KAOMOJI}"
    elif cat.activity == "cleaning":
        activityText = f"Current Activity: Cleaning {SPARKLES_KAOMOJI}"
    elif cat.activity == "running":
        activityText = f"Current Activity: Running {EXCITED_KAOMOJI}"
    else:
        activityText = f"Current Activity: {cat.activity.title()}"
    
    drawUnicodeLabel(activityText, popupX + popupW//2, activityY + 10, 
                    size=16, bold=True, fill='darkOrange')
    
    # action buttons
    buttonY = activityY + 60
    buttonWidth = 80
    buttonHeight = 40
    buttonSpacing = 20
    
    # calculate button positions to center them
    totalButtonWidth = buttonWidth * 3 + buttonSpacing * 2
    startX = popupX + (popupW - totalButtonWidth) // 2
    
    buttons = [
        {'name': 'feed', 'text': f'{EATING_KAOMOJI} Feed', 'color': 'lightGreen', 'x': startX},
        {'name': 'play', 'text': f'{EXCITED_KAOMOJI} Play', 'color': 'lightCoral', 'x': startX + buttonWidth + buttonSpacing},
        {'name': 'clean', 'text': f'{SPARKLES_KAOMOJI} Clean', 'color': 'lightBlue', 'x': startX + (buttonWidth + buttonSpacing) * 2}
    ]
    
    for button in buttons:
        # button shadow
        drawRect(button['x'] + 2, buttonY + 2, buttonWidth, buttonHeight, fill='gray', opacity=50)
        
        # main button
        buttonColor = 'lightGray' if app.draggingCat else button['color']
        drawRect(button['x'], buttonY, buttonWidth, buttonHeight, 
                fill=buttonColor, border='black', borderWidth=2)
        
        # button text
        drawLabel(button['text'], button['x'] + buttonWidth//2, buttonY + buttonHeight//2, 
                 size=10, bold=True, font='monospace')

def onMousePress(app, mouseX, mouseY):
    app.mouseX = mouseX
    app.mouseY = mouseY

    # update button positions before checking clicks
    updateActionButtons(app)

    # check popup button clicks FIRST if popup is open
    if app.selectedCat and hasattr(app, 'actionButtons'):
        for name, b in app.actionButtons.items():
            if b['x'] <= mouseX <= b['x'] + b['w'] and b['y'] <= mouseY <= b['y'] + b['h']:
                if name == 'feed':
                    app.selectedCat.feed()
                    return  # don't process other clicks
                elif name == 'play':
                    app.selectedCat.play()
                    return  # don't process other clicks
                elif name == 'clean':
                    app.selectedCat.clean()
                    return  # don't process other clicks
                elif name == 'close':
                    # ONLY close menu when red X is clicked
                    app.selectedCat = None
                    app.draggingCat = None
                    updateActionButtons(app)  # clear buttons when closing popup
                    return  # Don't process other clicks
        
        # if popup is open and click is inside popup area, don't select other cats
        popupX, popupY = app.popupX, app.popupY
        popupW, popupH = app.popupWidth, app.popupHeight
        if (popupX <= mouseX <= popupX + popupW and 
            popupY <= mouseY <= popupY + popupH):
            return  # Click was inside popup but not on a button, ignore it
    
    # Check furniture clicks BEFORE cat clicks
    for furniture in app.furniture:
        if furniture.isClicked(mouseX, mouseY):
            furniture.cycleVariant()
            print(f"Clicked {furniture.name}, now showing variant {furniture.currentVariant}")
            return  # don't process cat clicks if furniture was clicked

    # check if user clicked on a cat (works even if popup is open)
    for cat in app.cats:
        dist = ((mouseX - cat.x) ** 2 + (mouseY - cat.y) ** 2) ** 0.5
        if dist <= 50:
            app.selectedCat = cat
            app.draggingCat = cat
            app.dragStartTime = app.stepCounter
            cat.startDrag(mouseX, mouseY)
            updateActionButtons(app)  # update buttons for new selection
            return

def onMouseDrag(app, mouseX, mouseY):
    app.mouseX = mouseX
    app.mouseY = mouseY
    if app.draggingCat:
        app.draggingCat.updateDragPosition(mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    app.mouseX = mouseX
    app.mouseY = mouseY
    
    if app.draggingCat:
        dragDuration = app.stepCounter - app.dragStartTime
        
        if dragDuration >= 10:
            app.draggingCat.x = max(100, min(app.width - 100, app.draggingCat.x))
            app.draggingCat.y = max(100, min(app.height - 150, app.draggingCat.y))
        
        app.draggingCat.stopDrag()
        app.draggingCat = None

def onStep(app):
    if not app.paused:  # only update when not paused
        app.stepCounter += 1
        app.gameTime += 1
        
        if app.stepCounter % 30 == 0:
            for cat in app.cats:
                cat.updateStats()
                
                if app.stepCounter % 120 == 0:
                    cat.activity = "idle"

def onKeyPress(app, key):
    if key == 'p':
        app.paused = not app.paused
        # if app.paused:
        #     app.sound.pause()
        # else:
        #     app.sound.play(loop=True)
    elif key == 'r':  # press 'R' to make Elwin run
        elwin = None
        for cat in app.cats:
            if cat.name == "elwin":
                elwin = cat
                break
        if elwin:
            if not elwin.isRunning:
                print("Forcing Elwin to run!")
                elwin.startRunning()
            else:
                print("Elwin is already running!")
        else:
            print("Could not find Elwin!")
    elif key == 'f':  # press 'F' to show furniture info
        print("=== FURNITURE STATUS ===")
        for furniture in app.furniture:
            print(f"{furniture.name}: variant {furniture.currentVariant}/{len(furniture.variants)-1} - {furniture.variants[furniture.currentVariant] if furniture.currentVariant > 0 else 'original'}")

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(245, 245, 220))
    
    try:
        drawImage("images/basic_room2.png", 0, 0, width=app.width, height=app.height)
    except:
        drawLabel("Background image missing: images/basic_room2.png", app.width//2, 50, size=16, fill='red', font='monospace')

    # Draw furniture overlays after background but before cats
    drawFurnitureOverlays(app)

    # draw cats that aren't being dragged first
    catsToDraw = [cat for cat in app.cats if not cat.isBeingDragged]
    for cat in catsToDraw:
        cat.draw(app)
    
    # draw dragged cat on top
    if app.draggingCat:
        app.draggingCat.draw(app)
    
    # selection indicator
    if app.selectedCat and not app.selectedCat.isBeingDragged:
        drawCircle(app.selectedCat.x, app.selectedCat.y, 55, fill=None, border='cadetBlue', borderWidth=4, opacity=30)
    
    # draw the popup menu if a cat is selected
    if app.selectedCat:
        drawCatPopup(app, app.selectedCat)
    else:
        # instruction text with nice styling - using kaomoji
        instructionY = 100
        boxWidth = 680 
        drawRect(app.width//2 - boxWidth//2, instructionY - 50, boxWidth, 60, 
                fill='aliceBlue', border='cadetBlue', borderWidth=2, opacity=90)
        drawLabel(f"{HAPPY_KAOMOJI} Click on a cat to interact! {HAPPY_KAOMOJI}", app.width//2, instructionY-30, 
                 size=20, bold=True, fill='cadetBlue', font='monospace')
        drawLabel("Drag the cats around the room • Click the bed and cat post to recolor!", app.width//2, instructionY -5, 
                 size=16, fill='gray', font='monospace', bold=True)
    
    if app.draggingCat:
        # drag instruction with nice styling - using kaomoji
        dragY = app.height - 100
        drawRect(app.width//2 - 250, dragY - 20, 500, 60, 
                fill='lightYellow', border='orange', borderWidth=2, opacity=90)
        drawLabel(f"{EXCITED_KAOMOJI} Moving {app.draggingCat.name}! Release to place.", 
                 app.width//2, dragY, size=20, bold=True, fill='darkOrange', font='monospace')
        drawLabel("Place them on the floor area", app.width//2, dragY + 25, 
                 size=16, fill='gray', font='monospace')
    
    # optional debug mode to show furniture click areas
    # drawFurnitureClickAreas(app, showDebug=True)  # Set to True to see clickable areas
    
    # show pause indicator
    if app.paused:
        drawRect(app.width//2 - 100, 50, 200, 40, fill='black', opacity=70)
        drawLabel("PAUSED - Press 'P' to resume", app.width//2, 70, size=16, bold=True, fill='white', font='monospace')
    
    controlsX = app.width - 20
    controlsY = app.height - 30
    drawRect(controlsX - 200, controlsY - 55, 220, 85, fill='steelBlue', opacity=60)
    drawLabel("Extra Controls", controlsX - 90, controlsY - 40, size=18, bold=True, fill='white', font='monospace', align='center')
    drawLabel("P = Pause/Resume", controlsX - 90, controlsY - 15, size=14, fill='black', font='monospace', align='center')
    drawLabel("R = Make Elwin Run", controlsX - 90, controlsY + 5, size=14, fill='black', font='monospace', align='center')
    drawLabel("F = Furniture Info", controlsX - 90, controlsY + 25, size=14, fill='black', font='monospace', align='center')


def main():
    runApp()

if __name__ == "__main__":
    main()