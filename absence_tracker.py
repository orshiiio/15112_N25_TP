#############################################
##           arshia dabas 2025             ##
##   fundamentals of purr-ogramming cafe   ##
#############################################

import time
import os
import random

# "time" information from: https://docs.python.org/3/library/time.html
# idea for using a text file and rewriting over it was suggested by Elwin Li (incoming F25 TA) [all further implementation was my own]
# documentation for try/except from: https://www.w3schools.com/python/python_try_except.asp)
# please note that all the "random" print statements are actually largely for user-debugging and peace of mind (useful just to check)
# they serve no real in-game purpose and are not displayed other than in the console 

class AbsenceTracker:
    def __init__(self, app):
        self.app = app
        self.lastActiveTime = time.time()
        self.isActive = True
        self.absenceThresholds = {
            'short': 300,      # 5 minutes
            'medium': 1800,    # 30 minutes  
            'long': 3600,      # 1 hour
            'extended': 14400, # 4 hours
            'overnight': 28800 # 8 hours
        }
        self.saveFile = "last_active.txt"  # simple text file
        self.loadActivityData()
        
    def loadActivityData(self):
        # load last active time from text file
        try:
            if os.path.exists(self.saveFile):
                with open(self.saveFile, 'r') as f:
                    timeStr = f.read().strip()
                    if timeStr:  # Make sure file isn't empty
                        self.lastActiveTime = float(timeStr)
                        print(f"Loaded last active time: {self.lastActiveTime}")
                        print(f"That was {time.time() - self.lastActiveTime:.1f} seconds ago")
                    else:
                        print("File was empty, using current time")
                        self.lastActiveTime = time.time()
                        self.saveActivityData()
            else:
                print("No save file found, creating new one")
                self.lastActiveTime = time.time()
                self.saveActivityData()
        except Exception as e:
            print(f"Error loading activity data: {e}")
            self.lastActiveTime = time.time()
            self.saveActivityData()
    
    def saveActivityData(self):
        # save current activity time to text file
        try:
            with open(self.saveFile, 'w') as f:
                f.write(str(self.lastActiveTime))
            print(f"Saved activity time: {self.lastActiveTime}")
            return True
        except Exception as e:
            print(f"Error saving activity data: {e}")
            return False
    
    def updateActivity(self):
        # need to call this when there's actual user activity
        was_absent = not self.isActive
        old_time = self.lastActiveTime
        
        self.lastActiveTime = time.time()
        self.isActive = True
        
        # save immediately
        success = self.saveActivityData()
        print(f"Activity updated: {old_time:.1f} -> {self.lastActiveTime:.1f} (saved: {success})")
        
        if was_absent:
            self.onUserReturn()
    
    def getAbsenceTime(self):
        # get how long user has been inactive in seconds
        return time.time() - self.lastActiveTime
    
    def getAbsenceLevel(self):
        # categorized absence level
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
    
    def checkForAbsence(self):
        # check if user has been absent and trigger effects
        absenceTime = self.getAbsenceTime()
        # only trigger absence effects if we haven't already
        if self.isActive and absenceTime > self.absenceThresholds['short']:
            self.isActive = False
            self.onUserAbsence(absenceTime)
    
    def onUserAbsence(self, absenceTime):
        # handle what happens when user goes absent
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
        # effects for 5-30 minute absence
        print("Applying short absence effects...")
        for cat in self.app.cats:
            cat.happiness = max(0, cat.happiness - 5)
            cat.energy = max(0, cat.energy - 3)
    
    def applyMediumAbsenceEffects(self):
        # effects for 30 minute - 1 hour absence
        print("Applying medium absence effects...")
        for cat in self.app.cats:
            cat.happiness = max(0, cat.happiness - 10)
            cat.hunger = max(0, cat.hunger - 15)
            cat.energy = max(0, cat.energy - 8)
            cat.cleanliness = max(0, cat.cleanliness - 5)
            # cats start autonomous behaviors
            if cat.activity == "idle" and not cat.isRunning:
                if random.random() < 0.3:  # 30% chance
                    cat.startAutonomousActivity("wandering")
    
    def applyLongAbsenceEffects(self):
        # effects for 1-4 hour absence
        print("Applying long absence effects...")
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
        # effects for 4-8 hour absence
        print("Applying extended absence effects...")
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
        # effects for 8+ hour absence (overnight)
        print("Applying overnight absence effects...")
        for cat in self.app.cats:
            # simulate full day/night cycle
            cat.energy = min(100, cat.energy + 30)  # rested from sleeping
            cat.hunger = max(0, cat.hunger - 60)  # got hungry overnight
            cat.cleanliness = max(0, cat.cleanliness - 40)  # got messy
            cat.happiness = max(0, cat.happiness - 25)  #missed user but adapted
            
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