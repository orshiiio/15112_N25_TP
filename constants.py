#############################################
##           arshia dabas 2025             ##
##   fundamentals of purr-ogramming cafe   ##
#############################################

# i originally did a pip-install with this: https://pypi.org/project/py-kaomoji/
# the try/except format is from a previous Claude prompt (but i later learnt more about it from: https://www.w3schools.com/python/python_try_except.asp)
try:
    import kaomoji
    KAOMOJI_AVAILABLE = True
except ImportError:
    KAOMOJI_AVAILABLE = False

# complex Unicode kaomoji (ideal)
# taken from emojicombos.com/kaomoji
HAPPY_KAOMOJI = "(=^·ω·^=)"
SAD_KAOMOJI = "( ˘^˘ )"
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

# cat personality types
PERSONALITY_TYPES = {
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

# placeholder colors for cats when sprites fail to load
PLACEHOLDER_COLORS = {
    'churrio': (255, 165, 0),    # orange
    'beepaw': (128, 128, 128),   # gray
    'meeple': (255, 255, 255),   # white
    'elwin': (255, 228, 196)     # peach
}