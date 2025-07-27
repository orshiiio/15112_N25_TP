from cmu_graphics import *
import math
import time 

class Cat:
    def __init__(self, name, x, y, personality=None):
        self.name = name
        self.x = x
        self.y = y
        
        # store last valid position for placement restrictions
        self.last_valid_x = x
        self.last_valid_y = y
        
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
        
        # dragging state
        self.is_being_dragged = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.current_frame = 0
        self.animation_speed = 12 
        self.frame_timer = 0
        
        self.sprite_frames = {
            "idle_neutral": 6,    # all cats have ~6 frames for idle neutral
            "idle_happy": 8,      # all cats have ~8 frames for idle happy
            "idle_sad": 6,        # all cats have ~6 frames for idle sad
            "sleeping": 2,        # all cats have ~2 frames for sleeping
        }
        
        # personality 
        self.personality = personality or {
            'hunger_rate': 1.0,
            'energy_rate': 1.0,
            'messy_rate': 1.0,
            'social_need': 1.0,
            'playfulness': 1.0,
            'sleepiness': 1.0
        }

        self.is_selected = False

    def feed(self):
        self.hunger = min(100, self.hunger + 30)
        self.happiness = min(100, self.happiness + 10)
        self.activity = "eating"
        
    def play(self):
        if self.energy > 30:
            self.happiness = min(100, self.happiness + 25 * self.personality['playfulness'])
            self.energy = max(0, self.energy - 15)
            self.activity = "playing"
        
    def clean(self):
        self.cleanliness = min(100, self.cleanliness + 40)
        self.happiness = min(100, self.happiness + 5)
        self.activity = "cleaning"

    def start_drag(self, mouse_x, mouse_y):
        self.is_being_dragged = True
        self.drag_offset_x = mouse_x - self.x
        self.drag_offset_y = mouse_y - self.y
        self.happiness = max(0, self.happiness - 2)

    def update_drag_position(self, mouse_x, mouse_y):
        if self.is_being_dragged:
            self.x = mouse_x - self.drag_offset_x
            self.y = mouse_y - self.drag_offset_y

    def stop_drag(self):
        # when stopping drag, check if position is valid:
        if isValidPosition(self.x, self.y):
            # accept new position
            self.last_valid_x = self.x
            self.last_valid_y = self.y
        else:
            # revert to last valid position
            self.x = self.last_valid_x
            self.y = self.last_valid_y
        
        self.is_being_dragged = False
        self.happiness = min(100, self.happiness + 5)

    def get_current_animation_state(self):
        # check if sleeping first
        if self.is_sleeping:
            return "sleeping"
        # otherwise use idle animations based on mood
        elif self.mood == "happy":
            return "idle_happy"
        elif self.mood == "sad":
            return "idle_sad"
        else:
            return "idle_neutral"

    def update_animation(self):
        self.frame_timer += 1
        
        # different animation speeds for different states
        current_state = self.get_current_animation_state()
        if current_state == "sleeping":
            animation_speed = 20  # slower for peaceful sleeping
        elif current_state == "idle_happy":
            animation_speed = 8   # faster for happy/energetic cats
        else:
            animation_speed = self.animation_speed  # normal speed for neutral/sad
            
        if self.frame_timer >= animation_speed:
            self.frame_timer = 0
            
            # get current animation state and frame count
            max_frames = self.sprite_frames.get(current_state, 1)
            
            # cycle through frames
            self.current_frame = (self.current_frame + 1) % max_frames

    def get_sprite_path(self):
        current_state = self.get_current_animation_state()
        max_frames = self.sprite_frames.get(current_state, 1)
        
        # only use frame numbers if we have multiple frames
        if max_frames > 1:
            # build sprite filename: images/cats/elwin_idle_neutral_1.png
            frame_num = self.current_frame + 1  # 1-indexed
            sprite_filename = f"{self.name}_{current_state}_{frame_num}.png"
        else:
            # single frame, no number: e.g. images/cats/churrio_idle_happy.png
            sprite_filename = f"{self.name}_{current_state}.png"
            
        return f"images/cats/{sprite_filename}"

    def update_stats(self, time_multiplier=1):
        self.hunger = max(0, self.hunger - (0.1 * self.personality['hunger_rate'] * time_multiplier))
        self.energy = max(0, self.energy - (0.05 * self.personality['energy_rate'] * time_multiplier))
        self.cleanliness = max(0, self.cleanliness - (0.03 * self.personality['messy_rate'] * time_multiplier))

        if self.hunger < 20 or self.energy < 20 or self.cleanliness < 20:
            self.happiness = max(0, self.happiness - (0.15 * self.personality['social_need'] * time_multiplier))
        elif self.hunger > 80 and self.energy > 80 and self.cleanliness > 80:
            self.happiness = min(100, self.happiness + (0.05 * time_multiplier))

        avg_stat = (self.hunger + self.happiness + self.energy + self.cleanliness) / 4
        if avg_stat > 70:
            self.mood = "happy"
        elif avg_stat > 40:
            self.mood = "neutral"
        else:
            self.mood = "sad"

        self.is_sleeping = self.energy < 30

    def draw(self, app):
        self.animation_frame += 1
        self.update_animation()

        sprite_loaded = False

        try:
            sprite_path = self.get_sprite_path()
            drawImage(sprite_path, self.x, self.y, align='center', width=80, height=80)
            sprite_loaded = True
        except Exception as e:
            # debug: show what file it tried to load (only for elwin for now)
            if self.name == "elwin" and not sprite_loaded:
                attempted_path = self.get_sprite_path()
                print(f"Failed to load: {attempted_path}")  # This will print to console
            # fallback to old single sprite system
            try:
                if self.is_sleeping:
                    sprite_path = f"images/cats/{self.name}_sleeping.png"
                else:
                    sprite_path = f"images/cats/{self.name}_{self.mood}.png"

                drawImage(sprite_path, self.x, self.y, align='center', width=80, height=80)
                sprite_loaded = True
            except:
                # final fallback to basic cat sprite
                try:
                    sprite_path = f"images/cats/{self.name}.png"
                    drawImage(sprite_path, self.x, self.y, align='center', width=80, height=80)
                    sprite_loaded = True
                except:
                    pass

        # if no sprite loaded, show placeholder
        if not sprite_loaded:
            placeholder_colors = {
                'churrio': rgb(255, 165, 0),
                'beepaw': rgb(128, 128, 128),
                'meeple': rgb(255, 255, 255),
                'elwin': rgb(255, 228, 196)
            }
            color = placeholder_colors.get(self.name, rgb(200, 200, 200))

            drawRect(self.x - 40, self.y - 40, 80, 80, fill=color, border='black', 
                     borderWidth=2)
            drawLabel("SPRITE", self.x, self.y - 10, size=14, bold=True, font='monospace')
            drawLabel(self.name, self.x, self.y + 8, size=12, font='monospace')
            
            # show current animation state and frame for debugging
            current_state = self.get_current_animation_state()
            max_frames = self.sprite_frames.get(current_state, 1)
            if max_frames > 1:
                frame_info = f"{current_state}_f{self.current_frame + 1}/{max_frames}"
            else:
                frame_info = f"{current_state}"
            drawLabel(frame_info, self.x, self.y + 25, 
                     size=9, font='monospace')

        if self.is_being_dragged:
            drawCircle(self.x, self.y + 5, 45, fill='black', opacity=20)

        # emotion bubble logic
        emotion_path = None

        if self.is_being_dragged:
            emotion_path = "images/emotions/surprised.png"
        elif self.hunger < 25:
            emotion_path = "images/emotions/confused.png"
        elif self.cleanliness < 25:
            emotion_path = "images/emotions/sad.png"
        elif self.energy < 20:
            emotion_path = "images/emotions/neutral.png"
        elif self.activity == "eating":
            emotion_path = "images/emotions/content.png"
        elif self.activity == "playing":
            emotion_path = "images/emotions/wow.png"
        elif self.activity == "cleaning":
            emotion_path = "images/emotions/neutral.png"
        elif self.is_sleeping:
            emotion_path = "images/emotions/content.png"
        elif self.mood == "happy":
            if (self.animation_frame // 60) % 2 == 0:
                emotion_path = "images/emotions/happy.png"
            else:
                emotion_path = "images/emotions/happy2.png"
        elif self.mood == "sad":
            emotion_path = "images/emotions/sad.png"
        elif self.personality['social_need'] > 1.2 and self.happiness < 60:
            emotion_path = "images/emotions/meow.png"
        else:
            emotion_path = "images/emotions/neutral.png"

        bubble_x = self.x + 25
        bubble_y = self.y - 35

        if emotion_path:
            try:
                drawImage(emotion_path, bubble_x, bubble_y, align='center', width=50, height=50)
            except:
                try:
                    drawImage("images/emotions/neutral.png", bubble_x, bubble_y, align='center', width=50, height=50)
                except:
                    pass

        drawLabel(self.name, self.x, self.y + 60, size=14, bold=True, fill='black', font='monospace')

def create_cat_personalities():
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

# define allowed placement area for isometric room floor
def isValidPosition(x, y):
    # isometric room boundaries based on the floor area
    center_x = 1000  
    center_y = 650      
    width = 2000    
    height = 400      
    
    dx = x - center_x
    dy = y - center_y
    
    # diamond shape condition for the floor area
    return abs(dx) / (width / 2) + abs(dy) / (height / 2) <= 1

def onAppStart(app):
    app.width = 1920
    app.height = 1080
    app.step_counter = 0
    app.game_time = 0
    app.selected_cat = None
    
    # dragging state
    app.dragging_cat = None
    app.drag_start_time = 0
    app.mouse_x = 0
    app.mouse_y = 0
    
    personalities = create_cat_personalities()

    app.cats = [
        Cat("churrio", 800, 580, personalities['energetic']),
        Cat("beepaw", 1100, 520, personalities['independent']),
        Cat("meeple", 900, 650, personalities['clean']),
        Cat("elwin", 1200, 600, personalities['social']),
    ]
    
    app.buttons = {
        'feed': {'x': 100, 'y': 100, 'w': 120, 'h': 50, 'text': 'Feed Cat'},
        'play': {'x': 240, 'y': 100, 'w': 120, 'h': 50, 'text': 'Play'},
        'clean': {'x': 380, 'y': 100, 'w': 120, 'h': 50, 'text': 'Clean'},
    }

def onMousePress(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY
    
    # first check buttons if a cat is selected
    button_clicked = False
    if app.selected_cat:
        for button_name, button in app.buttons.items():
            if (button['x'] <= mouseX <= button['x'] + button['w'] and 
                button['y'] <= mouseY <= button['y'] + button['h']):
                
                if button_name == 'feed':
                    app.selected_cat.feed()
                elif button_name == 'play':
                    app.selected_cat.play()
                elif button_name == 'clean':
                    app.selected_cat.clean()
                button_clicked = True
                break
    
    # if user clicked a button, don't do anything else
    if button_clicked:
        return
    
    # check if clicked on a cat
    clicked_on_cat = False
    for cat in app.cats:
        distance = ((mouseX - cat.x) ** 2 + (mouseY - cat.y) ** 2) ** 0.5
        if distance <= 50:  # adjusted click radius for big cats
            app.selected_cat = cat
            app.dragging_cat = cat
            app.drag_start_time = app.step_counter
            cat.start_drag(mouseX, mouseY)
            clicked_on_cat = True
            break
    
    # if clicked outside any cat and a cat was selected, deselect
    if not clicked_on_cat and app.selected_cat is not None:
        app.selected_cat = None
        app.dragging_cat = None

def onMouseDrag(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY
    if app.dragging_cat:
        app.dragging_cat.update_drag_position(mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    app.mouse_x = mouseX
    app.mouse_y = mouseY
    
    if app.dragging_cat:
        drag_duration = app.step_counter - app.drag_start_time
        
        if drag_duration >= 10:
            app.dragging_cat.x = max(100, min(app.width - 100, app.dragging_cat.x))
            app.dragging_cat.y = max(100, min(app.height - 150, app.dragging_cat.y))
        
        app.dragging_cat.stop_drag()
        app.dragging_cat = None

def onStep(app):
    app.step_counter += 1
    app.game_time += 1
    
    if app.step_counter % 30 == 0:
        for cat in app.cats:
            cat.update_stats()
            
            if app.step_counter % 120 == 0:
                cat.activity = "idle"

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(245, 245, 220))
    
    try:
        drawImage("images/basic_room.png", 0, 0, width=app.width, height=app.height)
    except:
        drawLabel("Background image missing: images/basic_room.png", app.width//2, 50, size=16, fill='red', font='monospace')
    
    cats_to_draw = [cat for cat in app.cats if not cat.is_being_dragged]
    for cat in cats_to_draw:
        cat.draw(app)
    
    if app.dragging_cat:
        app.dragging_cat.draw(app)
    
    if app.selected_cat and not app.selected_cat.is_being_dragged:
        drawCircle(app.selected_cat.x, app.selected_cat.y, 55, fill=None, border='grey', borderWidth=3, opacity=20)
    
    if app.selected_cat:
        cat = app.selected_cat
        info_x, info_y = 100, 200
        
        drawRect(info_x - 10, info_y - 10, 400, 180, fill='white', border='black', borderWidth=2, opacity=90)
        drawLabel(f"Selected: {cat.name}", info_x, info_y, size=20, bold=True, align='left', font='monospace')
        
        stats_y = info_y + 40
        drawLabel(f"Hunger: {int(cat.hunger)}", info_x, stats_y, size=16, align='left', font='monospace')
        drawLabel(f"Happiness: {int(cat.happiness)}", info_x + 150, stats_y, size=16, align='left', font='monospace')
        drawLabel(f"Energy: {int(cat.energy)}", info_x, stats_y + 30, size=16, align='left', font='monospace')
        drawLabel(f"Cleanliness: {int(cat.cleanliness)}", info_x + 150, stats_y + 30, size=16, align='left', font='monospace')
        drawLabel(f"Mood: {cat.mood}", info_x, stats_y + 60, size=16, align='left', font='monospace')
        drawLabel(f"Activity: {cat.activity}", info_x + 150, stats_y + 60, size=16, align='left', font='monospace')
        
        for button_name, button in app.buttons.items():
            button_color = 'lightGray' if app.dragging_cat else 'lightBlue'
            drawRect(button['x'], button['y'], button['w'], button['h'], 
                    fill=button_color, border='black', borderWidth=2)
            drawLabel(button['text'], button['x'] + button['w']//2, button['y'] + button['h']//2, 
                     size=14, bold=True, font='monospace')
    else:
        drawLabel("Click on a cat to select it!", app.width//2, 100, size=24, bold=True, fill='black', font='monospace')
    
    if app.dragging_cat:
        drawLabel(f"Dragging {app.dragging_cat.name}! Release to place.", 
                 app.width//2, app.height - 100, size=20, bold=True, fill='yellow', font='monospace')

def main():
    runApp()

if __name__ == "__main__":
    main()