from cmu_graphics import *
from constants import *

def drawUnicodeLabel(text, x, y, size=16, bold=False, fill='black', align='center'):
    # i try to draw text with Unicode support by testing different font but it'll fall back to simple ASCII if Unicode fails
    # first try with different fonts that might support Unicode better
    # again this try/except format was from Claude (AI) but i did my own reserach on it after using it in "draw" [begining line 330]
    # the original prompt was "what format can i use to have a safety option for fonts in my python file"
    # i later learnt more about it from: https://www.w3schools.com/python/python_try_except.asp
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

# define allowed placement area for isometric room floor
# this took lots of trial and error since i'm not great at math
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

def drawStatBar(x, y, width, height, value, maxValue, color, label):
    # background bar
    drawRect(x, y, width, height, fill='lightGray', border='darkGray', borderWidth=1)
    # filled portion - add comprehensive safety checks
    if maxValue > 0 and value > 0:
        fillWidth = (value / maxValue) * width
        fillWidth = max(1, min(fillWidth, width))  # ensure minimum width of 1 (did this because it was bugging out without this check)
        drawRect(x, y, fillWidth, height, fill=color, border=None)
    # text overlay
    drawLabel(f"{label}: {int(value)}", x + width//2, y + height//2, 
             size=12, bold=True, fill='darkOliveGreen' if value > 50 else 'fireBrick', font='monospace')