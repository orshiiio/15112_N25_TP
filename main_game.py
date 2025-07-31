from cmu_graphics import *
from cat import Cat
from furniture import *
from absence_tracker import *
from utils import *
from constants import *

import random
import math
import time

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
    
    # absence tracker initialization
    app.absenceTracker = AbsenceTracker(app)
    app.welcomeMessage = None
    app.welcomeMessageTimer = 0

    # initialize absence popup variables
    app.awayTimeText = ""
    app.absenceLevelText = ""
    app.showAwayTime = False
    app.awayTimeTimer = 0

    # check if returning from absence
    absenceTime = app.absenceTracker.getAbsenceTime()
    if absenceTime > 30:  # Show popup if away for more than 30 seconds
        app.awayTimeText = app.absenceTracker.formatTime(absenceTime)
        app.absenceLevelText = app.absenceTracker.getAbsenceLevel()
        app.showAwayTime = True
        app.awayTimeTimer = 240  # Show for 8 seconds at 30fps
    
    # load background music ("cats in the cold - mage tears")
    # asked Joshua Wang how to do this (and looked at CMU graphics)
    app.backgroundMusic = Sound("sounds/background_music.mp3")
    app.musicEnabled = True
    app.musicPlaying = False

    # auto-start background music
    if app.musicEnabled:
        app.backgroundMusic.play(loop=True)
        app.musicPlaying = True

    app.cats = [
        Cat("churrio", 600, 600, PERSONALITY_TYPES['energetic']),
        Cat("beepaw", 300, 650, PERSONALITY_TYPES['independent']),
        Cat("meeple", 700, 700, PERSONALITY_TYPES['clean']),
        Cat("elwin", 1000, 700, PERSONALITY_TYPES['social']),
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

def updateActionButtons(app):
    # logic is based on what Mike Taylor discussed in lecture [07/29]
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
    app.absenceTracker.updateActivity()
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
                    return  # don't process other clicks
        
        # if popup is open and click is inside popup area, don't select other cats
        popupX, popupY = app.popupX, app.popupY
        popupW, popupH = app.popupWidth, app.popupHeight
        if (popupX <= mouseX <= popupX + popupW and 
            popupY <= mouseY <= popupY + popupH):
            return  # click was inside popup but not on a button, ignore it
    
    # check furniture clicks BEFORE cat clicks
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
    app.absenceTracker.updateActivity()
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
    app.stepCounter += 1
    app.gameTime += 1
    
    # handle away time popup timer
    if app.showAwayTime and app.awayTimeTimer > 0:
        app.awayTimeTimer -= 1
        if app.awayTimeTimer <= 0:
            app.showAwayTime = False
    
    # regular game updates
    if app.stepCounter % 30 == 0:
        for cat in app.cats:
            cat.updateStats()
            if app.stepCounter % 120 == 0:
                cat.activity = "idle"
    
    # check for absence periodically (but don't update activity)
    if app.stepCounter % 90 == 0:  # every 3 seconds
        app.absenceTracker.checkForAbsence()

def onKeyPress(app, key):
    app.absenceTracker.updateActivity()
    # pause/resume music with game
    if key == 'm':  # press 'M' to toggle music on/off
        if app.musicEnabled:
            if app.musicPlaying:
                app.backgroundMusic.pause()
                app.musicPlaying = False
                print("Music paused")
            else:
                app.backgroundMusic.play(loop=True)
                app.musicPlaying = True
                print("Music playing")
        else:
            print("Music not available")
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
    elif key == 'f':  # press 'F' to show furniture info in console
        print("=== FURNITURE STATUS ===")
        for furniture in app.furniture:
            print(f"{furniture.name}: variant {furniture.currentVariant}/{len(furniture.variants)-1} - {furniture.variants[furniture.currentVariant] if furniture.currentVariant > 0 else 'original'}")
    elif key == 't':  # test absence system
        print("=== TESTING ABSENCE SYSTEM ===")
        print(f"Current absence time: {app.absenceTracker.formatTime(app.absenceTracker.getAbsenceTime())}")
        print(f"Absence level: {app.absenceTracker.getAbsenceLevel()}")
        
        # reset to current time first, then simulate absence
        app.absenceTracker.lastActiveTime = time.time() - 3600  # set to exactly 1 hour ago
        app.absenceTracker.isActive = True  # reset active state
        app.absenceTracker.checkForAbsence()
        print("Simulated 1 hour absence!")

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(245, 245, 220))
    try:
        drawImage("images/basic_room2.png", 0, 0, width=app.width, height=app.height)
    except:
        drawLabel("Background image missing: images/basic_room2.png", app.width//2, 50, size=16, fill='red', font='monospace')

    # draw furniture overlays after background but before cats
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
    
    # draw away time popup
    if app.showAwayTime:
        boxWidth = 400
        boxHeight = 40
        x = app.width//2 - boxWidth//2
        y = 120
        
        # draw popup background
        drawRect(x, y, boxWidth, boxHeight, fill='lightYellow', 
                border='orange', borderWidth=3, opacity=85)
        level_text = app.absenceLevelText.capitalize()
        if level_text == "Active":
            level_text = "Just Arrived"
        
        # draw message
        message = f"You were away for {app.awayTimeText} ({level_text} Absence)"
        drawLabel(message, app.width//2, y + boxHeight//2, 
                 size=12, bold=True, fill='darkOrange', font='monospace')
    
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
    
    controlsX = app.width - 40
    controlsY = app.height - 70
    drawRect(controlsX - 200, controlsY - 55, 220, 135, fill='steelBlue', border='darkBlue', opacity=30)
    drawLabel("Extra Controls", controlsX - 90, controlsY - 40, size=18, bold=True, fill='white', font='monospace', align='center')
    drawLabel("R = Make Elwin Run", controlsX - 90, controlsY-5, size=14, fill='black', font='monospace', align='center')
    drawLabel("F = Furniture Info", controlsX - 90, controlsY + 15, size=14, fill='black', font='monospace', align='center')
    drawLabel("M = Pause/Resume Music", controlsX - 90, controlsY + 35, size=14, fill='black', font='monospace', align='center')
    drawLabel("T = Test Absence System", controlsX - 90, controlsY + 55, size=14, fill='black', font='monospace', align='center')

    # music status indicator
    if app.musicEnabled:
        musicStatus = "♪♫ ON" if app.musicPlaying else "♪♫ OFF"
        musicColor = 'lightGreen' if app.musicPlaying else 'lightCoral'
        drawRect(app.width - 80, 20, 60, 25, fill=musicColor, border='black', borderWidth=2, opacity=30)
        drawLabel(musicStatus, app.width - 50, 32, size=12, bold=True, fill='black', font='monospace')
    
def main():
    runApp()

if __name__ == "__main__":
    main()