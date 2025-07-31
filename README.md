# 🐈 15112_N25_TP: Fundamentals or Purr-ogramming Cafe  
A cozy and interactive Python-based simulation where you can care for cats with unique personalities in a customizable room environment.
---
## ✨ Features  

### 🐾 Cat Management System
- **Four Unique Cats**: Meet Churrio (energetic), Beepaw (independent), Meeple (clean), and Elwin (social)
- **Tamagotchi-Style Care**: Monitor and maintain each cat's hunger, happiness, energy, and cleanliness
- **Dynamic Moods**: Cats display happy, neutral, or sad moods based on their overall wellbeing
- **Personality-Driven Behaviors**: Each cat has unique rates for hunger, energy drain, messiness, and social needs

### 🎮 Interactive Gameplay
- **Drag & Drop**: Pick up and move cats around the room
- **Care Actions**: Feed, play with, and clean your cats through a popup interface
- **Behavioral Animations**: Watch cats run around randomly, sleep when tired, and express emotions through kaomojis
- **Real-Time Simulation**: Stats decrease over time, requiring active care and attention

### 🏠 Room Customization
- **Furniture Recoloring**: Click on the bed and cat post to cycle through different color variants
- **Isometric Room Design**: A cute perspective view with restricted placement areas for cats
- **Interactive Environment**: Furniture changes persist and affect the room's aesthetic

### 🎨 Visual Design
- **Sprite-Based Animation**: Multi-frame animations for different cat states (idle, happy, sad, sleeping, running)
- **Emotion Bubbles**: Visual indicators showing how each cat is feeling
- **Unicode Kaomoji**: Cute emoticons throughout the interface (with ASCII fallbacks)

---

## 🛠️ Technical Details  

### 🔧 Built With  
- **Python/CMU Graphics** Core logic and rendering  
- **OOP Design**: Modular, class-based architecture  
- **State Management**: Complex animation states, mood tracking, and behavioral systems
- **Event-Driven Architecture**: Mouse clicks, drag operations, and keyboard shortcuts (with collision/valid area checks)

### 🏗️ Architecture
- **Cat Class**: Manages individual cat stats, animations, personalities, and behaviors
- **FurniturePiece Class**: Handles clickable furniture areas and variant cycling
- **Personality System**: Configurable trait multipliers affecting cat behavior rates
- **Animation Engine**: Frame-based sprite animation with state-dependent timing
- **Absence System**: Monitors time away and applies realistic consequences to cat care

---

## 🎯 Gameplay Guide

### 🐱 Caring for Cats
1. **Click on any cat** to open their status popup
2. **Monitor their stats**: Hunger, Happiness, Energy, and Cleanliness (0-100 scale)
3. **Use action buttons**: Feed (🍽️), Play (🎉), Clean (✨) to maintain their wellbeing
4. **Watch their moods**: Happy cats show positive emotions, sad cats need attention

### 🏡 Room Management
- **Drag cats around**: Click and hold to move cats to different spots in the room
- **Recolor furniture**: Click on the bed or cat post to cycle through color variants
- **Valid placement**: Cats can only be placed in the diamond-shaped floor area

### ⌨️ Controls
- **m**: Pause/Resume the music
- **r**: Force Elwin to run around 
- **f**: Print furniture status to console
- **t**: Test 1 hour of user absence
- **z**: Debug mode with user interaction timestamps
- **y**: Test the absence pop-up
- **p**: Force the absence pop-up to appear
- **Mouse**: Click cats to interact, drag to move, click furniture to recolor

------

## 🚀 Getting Started

### 📦 Prerequisites
- Python 3.11+
- CMU Graphics library (`pip install cmu-graphics`)

### 🔧 Installation
1. Clone or download the project files
2. Ensure you have the required folder structure:
   ```
   project/
   ├── main_game.py
   ├── utils.py
   ├── constants.py
   ├── cat.py
   ├── absence_tracker.py
   ├── furniture.py
   ├── last_active.txt [this will be created upon running the game for the first time]
   ├── sounds/
   │   ├── background_music.mp3
   ├── images/
   │   ├── basic_room2.png
   │   ├── cats/
   │   │   └── [cat sprite files]
   │   ├── emotions/
   │   │   └── [emotion bubble images]
   │   └── furniture/
   │       └── [furniture variant PNGs]
   ```
3. Run `python main.py` to start the game

### 🎨 Asset Requirements
- **Background**: `images/basic_room2.png` (room background)
- **Cat Sprites**: Multi-frame animations for each cat state
- **Furniture Variants**: `bed_purple.png`, `post_green.png`, `post_red.png` in `images/furniture/`
- **Emotion Bubbles**: Various emotion states in `images/emotions/`

---

## 🎮 Gameplay Tips

### 🌟 Keeping Cats Happy
- **Feed regularly**: Hunger drops constantly, especially for energetic cats
- **Play when energetic**: High-energy cats need more interaction
- **Clean messy cats**: Some personalities get dirty faster than others
- **Monitor sleep**: Tired cats will sleep automatically, affecting their mood

### 🎨 Room Customization
- **Experiment with colors**: Click furniture multiple times to see all variants
- **Placement strategy**: Position cats where you can easily click them
- **Use debug mode**: Print information about the furniture and user activity within the console

---

## 📝 Update Log

### 🗓️ July 31, 2025
- Implemeted a collision check for cats to prevent position overlap
- Modified "Extra Controls" with all new features 
- Checked all game features/funtionalities 
- [PROJECT SUBMITTED FOR GRADING]

### 🗓️ July 30, 2025
- Added time tracking module
- Added pop-up for user "time-away" indication
- Added additional debugging keys
- Fixed issue with sprite/mood switching

### 🗓️ July 29, 2025
- Implemented furniture recoloring system with bed and cat post variants
- Added clickable furniture areas with visual debug mode
- Fixed positioning issues with furniture interaction
- Updated instruction text to include furniture recoloring

### 🗓️ July 26, 2025
- Implemented a better drag-and-drop functionality
- Fixed running behavior and animation system
- Added even more sprites/moods
- Created a better pop-up menu and buttons for visuals

### 🗓️ July 25, 2025
- Fixed basic animation system
- Added comprehensive cat personality traits
- Improved mood calculation and stat decay rates

### 🗓️ July 24, 2025
- Created initial cat care system with four unique cats
- Implemented sprite-based animation system
- Added tamagotchi-style stat management

---

## 🏆 Features in Development [in the Future]
- More furniture pieces and color variants
- Additional cat breeds and personalities
- Cafe rating and progression mechanics

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE] file for details.

---

## 🙏 Acknowledgments
- Built as a final project for Carnegie Mellon's **15-112**: Fundamentals of Programming
- Inspired by cozy simulation games like *Neko Atsume* and *Tamagotchi*
- Kaomoji emoticons from emojicombos.com
- Dedicated to my friends who share my love of cats 🐾
- Thank you to Elwin Li [@ebeetles] (https://www.github.com/ebeetles) who helped me create a format for this README and motivated me throughout this project 
