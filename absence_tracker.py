import time
import json
import os
import random

class AbsenceTracker:
    def __init__(self, app):
        self.app = app
        self.lastActiveTime = time.time()
        self.isActive = True
        self.absenceThresholds = {
            'short': 300,    # 5 minutes
            'medium': 1800,  # 30 minutes  
            'long': 3600,    # 1 hour
            'extended': 14400, # 4 hours
            'overnight': 28800 # 8 hours
        }
        self.saveFile = "user_activity.json"
        self.loadActivityData()
        
    def loadActivityData(self):
        try:
            if os.path.exists(self.saveFile):
                with open(self.saveFile, 'r') as f:
                    data = json.load(f)
                    self.lastActiveTime = data.get('lastActiveTime', time.time())
        except:
            self.lastActiveTime = time.time()
    
    def saveActivityData(self):
        # save activity
        try:
            data = {
                'lastActiveTime': self.lastActiveTime,
                'timestamp': time.time()
            }
            with open(self.saveFile, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def updateActivity(self):
        # call with user movement
        was_absent = not self.isActive
        
        self.lastActiveTime = time.time()
        self.isActive = True
        self.saveActivityData()  # save the activity data to file
        
        if was_absent:
            self.onUserReturn()

    def checkForAbsence(self):
        # check if user has been absent - call this periodically
        absenceTime = self.getAbsenceTime()
        if self.isActive and absenceTime > self.absenceThresholds['short']:
            self.isActive = False
            self.onUserAbsence(absenceTime)
    
    def getAbsenceTime(self):
        # get how long user has been inactive in seconds
        return time.time() - self.lastActiveTime
    
    def getAbsenceLevel(self):
        # get categorized absence level
        absenceTime = self.getAbsenceTime()
        
        if absenceTime < self.absenceThresholds['short']:
            return 'active'
        elif absenceTime < self.absenceThresholds['medium']:
            return 'short'
        elif absenceTime < self.absenceThresholds['long']:
            return 'medium'
        elif absenceTime < self.absenceThresholds['extended']:
            return 'long'  
        elif absenceTime < self.absenceThresholds['overnight']:
            return 'extended'
        else:
            return 'overnight'
    
    def onUserAbsence(self, absenceTime):
        # what happens when user goes absent
        level = self.getAbsenceLevel()
        
        print(f"User absent for {absenceTime:.0f} seconds (level: {level})")
        
        # apply effects based on absence level
        if level == 'short':
            self.applyShortAbsenceEffects()
        elif level == 'medium':
            self.applyMediumAbsenceEffects()
        elif level == 'long':
            self.applyLongAbsenceEffects()
        elif level == 'extended':
            self.applyExtendedAbsenceEffects()
        elif level == 'overnight':
            self.applyOvernightAbsenceEffects()
    
    def onUserReturn(self):
        absenceTime = self.getAbsenceTime()
        level = self.getAbsenceLevel()
        print(f"Welcome back! You were away for {self.formatTime(absenceTime)}")
    
    def applyShortAbsenceEffects(self):
        for cat in self.app.cats:
            cat.happiness = max(0, cat.happiness - 5)
            cat.energy = max(0, cat.energy - 3)
    
    def applyMediumAbsenceEffects(self):
        for cat in self.app.cats:
            cat.happiness = max(0, cat.happiness - 10)
            cat.hunger = max(0, cat.hunger - 15)
            cat.energy = max(0, cat.energy - 8)
            cat.cleanliness = max(0, cat.cleanliness - 5)
            
            # Cats start autonomous behaviors
            if cat.activity == "idle" and not cat.isRunning:
                if random.random() < 0.3:  # 30% chance
                    cat.startAutonomousActivity("wandering")
    
    def applyLongAbsenceEffects(self):
        for cat in self.app.cats:
            cat.happiness = max(0, cat.happiness - 20)
            cat.hunger = max(0, cat.hunger - 30)
            cat.energy = max(0, cat.energy - 15)
            cat.cleanliness = max(0, cat.cleanliness - 15)
            
            # more autonomous behaviors
            if cat.activity == "idle" and not cat.isRunning:
                activities = ["wandering", "playing", "self-grooming"]
                cat.startAutonomousActivity(random.choice(activities))
    
    def applyExtendedAbsenceEffects(self):
        for cat in self.app.cats:
            cat.happiness = max(0, cat.happiness - 35)
            cat.hunger = max(0, cat.hunger - 50)
            cat.energy = max(0, cat.energy - 25)
            cat.cleanliness = max(0, cat.cleanliness - 30)
            
            # survival behaviors based on needs
            if cat.hunger < 30:
                cat.startAutonomousActivity("foraging")
            elif cat.energy < 20:
                cat.startAutonomousActivity("sleeping")
            elif cat.cleanliness < 25:
                cat.startAutonomousActivity("self-grooming")
    
    def applyOvernightAbsenceEffects(self):
        for cat in self.app.cats:
            # simulate full day/night cycle
            cat.energy = min(100, cat.energy + 30)  # rested from sleeping
            cat.hunger = max(0, cat.hunger - 60)  # got hungry overnight
            cat.cleanliness = max(0, cat.cleanliness - 40)  # got messy
            cat.happiness = max(0, cat.happiness - 25)  # missed you but adapted
            
            # set appropriate activity for their current state
            if cat.hunger < 20:
                cat.startAutonomousActivity("foraging")
            elif cat.cleanliness < 30:
                cat.startAutonomousActivity("self-grooming")
            else:
                cat.startAutonomousActivity("wandering")
    
    def formatTime(self, seconds):
        # convert seconds to readable time format
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            if hours > 0:
                return f"{days}d {hours}h"
            return f"{days} day{'s' if days != 1 else ''}"