from cmu_graphics import *
import random

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
        
        # all cat sprites/room sprites from itch.io (artist: ToffeeCraft)
        self.spriteFrames = {
            "idle_neutral": 6,    # all cats have ~6 frames for idle neutral
            "idle_happy": 8,      # all cats have ~8 frames for idle happy
            "sad": 14,        # all cats have ~6 frames for idle sad
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

        # absence tracker support
        self.autonomousTimer = 0

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
            threshold = 1 * self.personality['playfulness']
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
        # check mood BEFORE sleeping - sad cats show sad even when tired
        elif self.mood == "happy":
            return "idle_happy"
        elif self.mood == "sad":
            return "sad"
        # check if sleeping (only if mood is neutral)
        elif self.isSleeping and not self.isRunning:
            return "sleeping"
        else:
            return "idle_neutral"

    def updateAnimation(self):
        self.frameTimer += 1
        # different animation speeds for different states
        # this was mostly trial and error 
        currentState = self.getCurrentAnimationState()
        if currentState == "dangling":
            animationSpeed = 15  # moderate speed for dangling animation
        elif currentState == "running":
            animationSpeed = 5  # faster running 
        elif currentState == "sleeping":
            animationSpeed = 20  # slower for peaceful sleeping
        elif currentState == "idle_happy":
            animationSpeed = 8   # faster for happy/energetic cats
        elif currentState == "sad":
            animationSpeed = 5
        else:
            animationSpeed = self.animationSpeed  # normal-ish speed for neutral/sad
            
        if self.frameTimer >= animationSpeed:
            self.frameTimer = 0
            # get current animation state and frame count
            maxFrames = self.spriteFrames.get(currentState, 1)
            # cycle through frames
            self.currentFrame = (self.currentFrame + 1) % maxFrames

    # initially was unsure how to handle getting sprites but was helped by students Josie Peller and Joshua Wang
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

    def startAutonomousActivity(self, activity):
        self.activity = activity
        self.autonomousTimer = random.randint(60, 180)  # 2-6 seconds at 30fps
        
        if activity == "wandering":
            # Move to a random valid location
            attempts = 0
            while attempts < 10:
                targetX = random.randint(300, 900)
                targetY = random.randint(500, 800)
                if isValidPosition(targetX, targetY):
                    self.x = targetX
                    self.y = targetY
                    break
                attempts += 1
                
        elif activity == "foraging":
            # Slowly recover hunger
            self.hunger = min(100, self.hunger + 10)
            
        elif activity == "self-grooming":
            # Improve cleanliness
            self.cleanliness = min(100, self.cleanliness + 15)
            
        elif activity == "playing":
            # Boost happiness but use energy
            self.happiness = min(100, self.happiness + 8)
            self.energy = max(0, self.energy - 5)
    
    def updateAutonomousBehavior(self):
        """Update autonomous behavior timers"""
        if self.autonomousTimer > 0:
            self.autonomousTimer -= 1
            if self.autonomousTimer <= 0:
                self.activity = "idle"

    def draw(self, app):
        from constants import PLACEHOLDER_COLORS
        self.animationFrame += 1
        self.updateAnimation()
        self.updateRunning()  # add running behavior
        self.updateAutonomousBehavior()  # update autonomous behaviors
        spriteLoaded = False
    
        # first we try the primary sprite system
        if not spriteLoaded:
            try:
                spritePath = self.getSpritePath()
                drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
                spriteLoaded = True
            except Exception as e:
                pass
        # there were initially bugs with loading sprites so i asked claude (AI) 
        # "how can i trial a sprite path/show something else if my sprite has a bug"
        # and i was recommended this try/except format and the rest was my own work
        # first we try the primary sprite system
        if not spriteLoaded:
            try:
                spritePath = self.getSpritePath()
                drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
                spriteLoaded = True
            except:
                pass
        # then fallback to mood-based sprites
        if not spriteLoaded:
            try:
                if self.isSleeping:
                    spritePath = f"images/cats/{self.name}_sleeping.png"
                else:
                    spritePath = f"images/cats/{self.name}_{self.mood}.png"
                drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
                spriteLoaded = True
            except:
                pass
        # final fallback to basic sprite
        if not spriteLoaded:
            try:
                spritePath = f"images/cats/{self.name}.png"
                drawImage(spritePath, self.x, self.y, align='center', width=80, height=80)
                spriteLoaded = True
            except:
                pass
        # if no sprite loaded, show placeholder
        if not spriteLoaded:
            color = rgb(*PLACEHOLDER_COLORS.get(self.name, (200, 200, 200)))

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