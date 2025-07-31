from cmu_graphics import *

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

def createFurniturePieces():
    # idea is to define clickable furniture areas and their variants
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
        # i might add more furniture pieces later
        # furniturePiece(
        #     name="bookshelf",
        #     x=100, y=200, width=60, height=150,
        #     variants=["original", "bookshelf_oak.png", "bookshelf_cherry.png"]
        # ),
    ]
    return furniture

def drawFurnitureOverlays(app):
    for furniture in app.furniture:
        variantPath = furniture.getCurrentVariantPath()
        if variantPath:  # only draw if not using original
            drawImage(variantPath, furniture.x, furniture.y, 
                         width=furniture.width, height=furniture.height)