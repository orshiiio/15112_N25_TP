from cmu_graphics import *
import math
import time 

class Cat:
    def __init__(self, name, x, y, color, personality=None):
        self.name = name
        self.x = x
        self.y = y
        self.color = color

        self.is_being_dragged = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0     
        
        # tamagotchi-style stats (0-100)
        self.hunger = 50
        self.happiness = 50
        self.energy = 50
        self.cleanliness = 50
        
        # animation and behavior
        self.mood = "neutral"
        self.animation_frame = 0
        self.last_action_time = 0
        self.is_sleeping = False
        self.activity = "idle"
        
        # player interaction
        self.being_petted = False
        self.customer_satisfaction = 0
        
        # personality will show how quickly stats decay and how much they gain from actions
        self.personality = personality or {
            'hunger_rate': 1.0,      # how quickly hunger decreases
            'energy_rate': 1.0,      # how quickly energy decreases  
            'messy_rate': 1.0,       # how quickly cleanliness decreases
            'social_need': 1.0,      # how much happiness is affected by neglect
            'playfulness': 1.0,      # how much they enjoy playing
            'sleepiness': 1.0        # how much they like to rest
        }

    def feed(self):
        base_hunger_gain = 30
        base_happiness_gain = 10
        self.hunger = min(100, self.hunger + base_hunger_gain)
        self.happiness = min(100, self.happiness + base_happiness_gain)
        self.activity = "eating"
        
    def play(self):
        if self.energy > 30:
            base_happiness_gain = 25 * self.personality['playfulness']
            base_energy_cost = 15
            self.happiness = min(100, self.happiness + base_happiness_gain)
            self.energy = max(0, self.energy - base_energy_cost)
            self.activity = "playing"
        
    def clean(self):
        base_clean_gain = 40
        base_happiness_gain = 5
        self.cleanliness = min(100, self.cleanliness + base_clean_gain)
        self.happiness = min(100, self.happiness + base_happiness_gain)
        self.activity = "cleaning"
    
    def start_drag(self, mouse_x, mouse_y):
        # start dragging cat 
        self.is_being_dragged = True
        self.drag_offset_x = mouse_x - self.x
        self.drag_offset_y = mouse_y - self.y
        # cats might be slightly annoyed by being picked up LOL
        self.happiness = max(0, self.happiness - 2)
        
    def update_drag_position(self, mouse_x, mouse_y):
        # to update position
        if self.is_being_dragged:
            self.x = mouse_x - self.drag_offset_x
            self.y = mouse_y - self.drag_offset_y
            
    def stop_drag(self):
        # stop dragginga and release cat
        self.is_being_dragged = False
        # cats may or may not be happy to be put down in a new spot
        self.happiness = min(100, self.happiness + 5)

    def update_stats(self, time_multiplier=1):
        # plan is to gradually decrease stats over time (like a real tamagotchi)
        # use personality to modify decay rates
        self.hunger = max(0, self.hunger - (0.1 * self.personality['hunger_rate'] * time_multiplier))
        self.energy = max(0, self.energy - (0.05 * self.personality['energy_rate'] * time_multiplier))
        self.cleanliness = max(0, self.cleanliness - (0.03 * self.personality['messy_rate'] * time_multiplier))
        
        # happiness depends on other stats and social needs
        if self.hunger < 20 or self.energy < 20 or self.cleanliness < 20:
            self.happiness = max(0, self.happiness - (0.15 * self.personality['social_need'] * time_multiplier))
        elif self.hunger > 80 and self.energy > 80 and self.cleanliness > 80:
            self.happiness = min(100, self.happiness + (0.05 * time_multiplier))
        
        # update mood based on stats
        avg_stat = (self.hunger + self.happiness + self.energy + self.cleanliness) / 4
        if avg_stat > 70:
            self.mood = "happy"
        elif avg_stat > 40:
            self.mood = "neutral"
        else:
            self.mood = "sad"
            
        # "auto-sleep" when energy is low
        self.is_sleeping = self.energy < 30

    def draw(self, app):
        self.animation_frame += 1
        sprite_loaded = False
        
        # Method 1: Try mood-based sprites (recommended)
        try:
            if self.is_sleeping:
                sprite_path = f"images/cats/{self.name}_sleeping.png"
            else:
                sprite_path = f"images/cats/{self.name}_{self.mood}.png"
            
            drawImage(sprite_path, self.x, self.y, align='center')
            sprite_loaded = True
        except:
            pass
        # dragging indicator
        if self.is_being_dragged:
            # subtle shadow or glow effect
            drawCircle(self.x, self.y + 5, 35, fill='black', opacity=20)
            drawLabel("✋", self.x + 45, self.y - 45, size=20)  # Hand icon
        
        # draw activity indicators
        if self.activity == "eating":
            drawLabel("🍽️", self.x + 35, self.y - 20, size=16)
        elif self.activity == "playing":
            drawLabel("🎾", self.x + 35, self.y - 20, size=16)
        elif self.activity == "cleaning":
            drawLabel("🫧", self.x - 35, self.y - 20, size=16)
        
        # personality icon
        personality_icon = ""
        if self.personality['playfulness'] > 1.2:
            personality_icon = "🎾"  
        elif self.personality['sleepiness'] > 1.2:
            personality_icon = "😴"  
        elif self.personality['social_need'] > 1.2:
            personality_icon = "💕"  
        elif self.personality['messy_rate'] < 0.8:
            personality_icon = "✨" 
        
        if personality_icon:
            drawLabel(personality_icon, self.x + 20, self.y + 35, size=12)
        
        # cat name below sprite
        drawLabel(self.name, self.x, self.y + 50, size=14, bold=True, fill='black')
        
        # critical status warnings
        if self.hunger < 25:
            drawLabel("😿", self.x - 40, self.y - 40, size=20)
        if self.cleanliness < 25:
            drawLabel("💨", self.x + 40, self.y - 40, size=20)


def create_cat_personalities():
    # an attempt to create different personality types for different cats
    personalities = {
        'lazy': {
            'hunger_rate': 0.8, 'energy_rate': 1.5, 'messy_rate': 1.2,
            'social_need': 0.8, 'playfulness': 0.6, 'sleepiness': 1.5
        },
        'energetic': {
            'hunger_rate': 1.3, 'energy_rate': 0.7, 'messy_rate': 1.3,
            'social_need': 1.2, 'playfulness': 1.8, 'sleepiness': 0.6
        },
        'clean': {
            'hunger_rate': 1.0, 'energy_rate': 1.0, 'messy_rate': 0.5,
            'social_need': 1.0, 'playfulness': 1.0, 'sleepiness': 1.0
        },
        'social': {
            'hunger_rate': 1.0, 'energy_rate': 1.0, 'messy_rate': 1.0,
            'social_need': 1.8, 'playfulness': 1.3, 'sleepiness': 0.8
        },
        'independent': {
            'hunger_rate': 0.9, 'energy_rate': 0.9, 'messy_rate': 0.9,
            'social_need': 0.5, 'playfulness': 0.8, 'sleepiness': 1.1
        }
    }
    return personalities

def onAppStart(app):
    app.width = 512*2
    app.height = 512*2
    app.step_counter = 0
    app.game_time = 0
    app.selected_cat = None
    app.backgroundImage = 'images/basic_room.png'
    
    # Dragging state
    app.dragging_cat = None
    app.drag_start_time = 0
    app.mouse_x = 0
    app.mouse_y = 0
    personalities = create_cat_personalities()

    app.cats = [
        Cat("churrio", 450, 450, personalities['energetic']),   # orange energetic cat
        Cat("beepaw", 500, 400, personalities['independent']),  # grey independent cat  
        Cat("meeple", 400, 500, personalities['clean']),        # white clean cat
        Cat("elwin", 600, 450, personalities['social']),        # cream social cat 
    ]
    
    # basic action buttons
    app.buttons = {
        'feed': {'x': 50, 'y': 50, 'w': 100, 'h': 40, 'text': 'Feed Cat'},
        'play': {'x': 160, 'y': 50, 'w': 100, 'h': 40, 'text': 'Play'},
        'clean': {'x': 270, 'y': 50, 'w': 100, 'h': 40, 'text': 'Clean'},
    }

def onMousePress(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY
    
    # check if clicking on a cat
    for cat in app.cats:
        distance = ((mouseX - cat.x) ** 2 + (mouseY - cat.y) ** 2) ** 0.5
        if distance <= 40:  # Increased click area
            app.selected_cat = cat
            app.dragging_cat = cat
            app.drag_start_time = app.step_counter
            cat.start_drag(mouseX, mouseY)
            return
    
    # check button clicks (only if not clicking on a cat)
    if app.selected_cat and not app.dragging_cat:
        for button_name, button in app.buttons.items():
            if (button['x'] <= mouseX <= button['x'] + button['w'] and 
                button['y'] <= mouseY <= button['y'] + button['h']):
                
                if button_name == 'feed':
                    app.selected_cat.feed()
                elif button_name == 'play':
                    app.selected_cat.play()
                elif button_name == 'clean':
                    app.selected_cat.clean()
                break

def onMouseDrag(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY
    
    # if we're dragging a cat = update its position
    if app.dragging_cat:
        app.dragging_cat.update_drag_position(mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY
    
    # If we were dragging a cat, stop dragging
    if app.dragging_cat:
        # check if this was a quick click (selection) vs a drag (movement)
        drag_duration = app.step_counter - app.drag_start_time
        
        if drag_duration < 10:  # Quick click (less than ~0.17 seconds)
            # just select the cat, don't move it
            app.dragging_cat.x = app.dragging_cat.x  # Keep current position
            app.dragging_cat.y = app.dragging_cat.y
        else:
            # actual drag - make sure cat stays within bounds
            app.dragging_cat.x = max(50, min(app.width - 50, app.dragging_cat.x))
            app.dragging_cat.y = max(50, min(app.height - 100, app.dragging_cat.y))
        
        app.dragging_cat.stop_drag()
        app.dragging_cat = None

def onMouseMove(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY

def onStep(app):
    app.step_counter += 1
    app.game_time += 1
    
    # update cats every 30 steps (every 0.5 seconds at 60 FPS)
    if app.step_counter % 30 == 0:
        for cat in app.cats:
            cat.update_stats()
            
            # Reset activity after some time
            if app.step_counter % 120 == 0:  # Every 2 seconds
                cat.activity = "idle"

def redrawAll(app):
    # draw background
    try:
        drawImage(app.backgroundImage, 0, 0, width=app.width, height=app.height)
    except:
        # Fallback background if image not found
        drawRect(0, 0, app.width, app.height, fill=rgb(245, 245, 220))
        drawLabel("Background image not found: images/basic_room.png", app.width//2, 100, size=16, fill='red')
    
    # draw cats (dragging cat drawn last to appear on top)
    cats_to_draw = [cat for cat in app.cats if not cat.is_being_dragged]
    for cat in cats_to_draw:
        cat.draw(app)
    
    # draw dragging cat on top
    if app.dragging_cat:
        app.dragging_cat.draw(app)
    
    # draw selection indicator (but not if cat is being dragged)
    if app.selected_cat and not app.selected_cat.is_being_dragged:
        drawCircle(app.selected_cat.x, app.selected_cat.y, 50, fill=None, border='yellow', borderWidth=3)
    
    # draw UI
    if app.selected_cat:
        # selected cat info
        cat = app.selected_cat
        info_x, info_y = 50, 120
        
        drawRect(info_x - 10, info_y - 10, 350, 150, fill='white', border='black', borderWidth=2, opacity=90)
        drawLabel(f"Selected: {cat.name}", info_x, info_y, size=18, bold=True, align='left')
        
        # Stats
        stats_y = info_y + 30
        drawLabel(f"Hunger: {int(cat.hunger)}", info_x, stats_y, size=14, align='left')
        drawLabel(f"Happiness: {int(cat.happiness)}", info_x + 120, stats_y, size=14, align='left')
        drawLabel(f"Energy: {int(cat.energy)}", info_x, stats_y + 25, size=14, align='left')
        drawLabel(f"Cleanliness: {int(cat.cleanliness)}", info_x + 120, stats_y + 25, size=14, align='left')
        drawLabel(f"Mood: {cat.mood}", info_x, stats_y + 50, size=14, align='left')
        drawLabel(f"Activity: {cat.activity}", info_x + 120, stats_y + 50, size=14, align='left')
        
        # action buttons (disabled while dragging)
        button_opacity = 50 if app.dragging_cat else 100
        for button_name, button in app.buttons.items():
            button_color = 'lightGray' if app.dragging_cat else 'lightBlue'
            drawRect(button['x'], button['y'], button['w'], button['h'], 
                    fill=button_color, border='black', borderWidth=2, opacity=button_opacity)
            drawLabel(button['text'], button['x'] + button['w']//2, button['y'] + button['h']//2, 
                     size=12, bold=True, opacity=button_opacity)
    else:
        drawLabel("Click on a cat to select it!", app.width//2, 50, size=20, bold=True, fill='white')
    
    # dragging instructions
    if app.dragging_cat:
        drawLabel(f"Dragging {app.dragging_cat.name}! Release to place.", 
                 app.width//2, app.height - 50, size=16, bold=True, fill='yellow')
    else:
        drawLabel("💡 Click and drag cats to move them around!", 
                 app.width//2, app.height - 30, size=14, fill='lightBlue')

def main():
    runApp()
    
main()