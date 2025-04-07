import random

alphabet = list()

class Board:
    """
    Represents the Scrabble game board with a 15x15 grid of cells.
    Handles board navigation and position queries.
    """
    def __init__(self, multiplier_file) -> None:
        """
        Initialize the game board with multipliers loaded from a file.
        
        Args:
            multiplier_file: Path to file containing board multipliers
        """
        multipliers = self.read_multipliers(multiplier_file)
        self.board = [[Cell((i, j), multipliers[i][j]) for j in range(15)] for i in range(15)]

    def read_multipliers(self, filename):
        """
        Read board multipliers from a file.
        
        Args:
            filename: Path to the multiplier configuration file
            
        Returns:
            2D array of multiplier values
        """
        with open(filename, 'r') as f:
            return [[num for num in line.split(',')] for line in f.read().split('\n')]

    def all_positions(self):
        """
        Get all valid positions on the board.
        
        Returns:
            List of (row, column) tuples representing all positions
        """
        positions = []
        for i in range(15):
            for j in range(15):
                positions.append((i, j))
        return positions

    def left(self, pos):
        """Get the position to the left of the given position."""
        i, j = pos
        return i, j - 1
    
    def right(self, pos):
        """Get the position to the right of the given position."""
        i, j = pos
        return i, j + 1

    def up(self, pos):
        """Get the position above the given position."""
        i, j = pos
        return i - 1, j
    
    def down(self, pos):
        """Get the position below the given position."""
        i, j = pos
        return i + 1, j
    
    def before(self, pos, is_horizontal):
        """
        Get the position before the given position in the specified direction.
        
        Args:
            pos: Current position (row, column)
            is_horizontal: If True, get position to the left; if False, get position above
            
        Returns:
            Position tuple (row, column)
        """
        if is_horizontal:
            return self.left(pos)
        else:
            return self.up(pos)
        
    def after(self, pos, is_horizontal):
        """
        Get the position after the given position in the specified direction.
        
        Args:
            pos: Current position (row, column)
            is_horizontal: If True, get position to the right; if False, get position below
            
        Returns:
            Position tuple (row, column)
        """
        if is_horizontal:
            return self.right(pos)
        else:
            return self.down(pos)
        
    def has_left(self, pos):
        """
        Check if the position to the left contains a tile.
        
        Args:
            pos: Current position (row, column)
            
        Returns:
            True if there is a tile to the left, False otherwise
        """
        i, j = pos
        return not((j - 1) < 0 or self.is_empty((i, j - 1)))
    
    def has_right(self, pos):
        """
        Check if the position to the right contains a tile.
        
        Args:
            pos: Current position (row, column)
            
        Returns:
            True if there is a tile to the right, False otherwise
        """
        i, j = pos
        return not((j + 1) > 14 or self.is_empty((i, j + 1)))
    
    def has_up(self, pos):
        """
        Check if the position above contains a tile.
        
        Args:
            pos: Current position (row, column)
            
        Returns:
            True if there is a tile above, False otherwise
        """
        i, j = pos
        return not((i - 1) < 0 or self.is_empty((i - 1, j)))
    
    def has_down(self, pos):
        """
        Check if the position below contains a tile.
        
        Args:
            pos: Current position (row, column)
            
        Returns:
            True if there is a tile below, False otherwise
        """
        i, j = pos
        return not((i + 1) > 14 or self.is_empty((i + 1, j)))
    
    def has_before(self, pos, is_horizontal):
        """
        Check if the position before in the specified direction contains a tile.
        
        Args:
            pos: Current position (row, column)
            is_horizontal: If True, check to the left; if False, check above
            
        Returns:
            True if there is a tile in the before position, False otherwise
        """
        if is_horizontal:
            return self.has_left(pos)
        else:
            return self.has_up(pos)
        
    def has_after(self, pos, is_horizontal):
        """
        Check if the position after in the specified direction contains a tile.
        
        Args:
            pos: Current position (row, column)
            is_horizontal: If True, check to the right; if False, check below
            
        Returns:
            True if there is a tile in the after position, False otherwise
        """
        if is_horizontal:
            return self.has_right(pos)
        else:
            return self.has_down(pos)

    def is_inbounds(self, pos):
        """
        Check if a position is within the board boundaries.
        
        Args:
            pos: Position to check (row, column)
            
        Returns:
            True if the position is within bounds, False otherwise
        """
        i, j = pos
        return i >= 0 and i <= 14 and j >= 0 and j <= 14 

    def is_empty(self, pos, allow_draft=True):
        """
        Check if a position on the board is empty.
        
        Args:
            pos: Position to check (row, column)
            allow_draft: If True, drafted tiles are considered placed; if False, they're considered empty
            
        Returns:
            True if the position is empty, False otherwise
        """
        i, j = pos
        tile = self.board[i][j].tile
        return (tile is None) if allow_draft else (tile is None or tile.draft)
    
    def get_pos(self, pos):
        """
        Get the cell at a specific position.
        
        Args:
            pos: Position (row, column)
            
        Returns:
            Cell object at the specified position
        """
        return self.board[pos[0]][pos[1]]
          

class Cell:
    """
    Represents a single cell on the Scrabble board.
    Contains information about position, multiplier, and the tile placed on it.
    """
    def __init__(self, position, multiplier) -> None:
        """
        Initialize a cell.
        
        Args:
            position: (row, column) tuple
            multiplier: Score multiplier for this cell (e.g., "DW", "TL")
        """
        self.position = position
        self.multiplier = multiplier
        self.tile = None
    
    def is_empty(self):
        """
        Check if the cell has no tile.
        
        Returns:
            True if the cell is empty, False otherwise
        """
        return self.tile is None
    

class Tile:
    """
    Represents a letter tile in the Scrabble game.
    Holds the letter, point value, and draft status.
    """
    def __init__(self, letter, point) -> None:
        """
        Initialize a tile.
        
        Args:
            letter: Letter on the tile
            point: Point value of the tile
        """
        self.letter = letter
        self.point = point
        self.draft = False  # True when the tile is temporarily placed but not yet confirmed


class Pouch: 
    """
    Represents the bag/pouch of tiles in the Scrabble game.
    Handles tile storage and random drawing.
    """
    def __init__(self, tile_file) -> None:
        """
        Initialize the pouch with tiles from a configuration file.
        
        Args:
            tile_file: Path to file with tile definitions
        """
        self.tiles = list()
        self.init_tiles(tile_file)

    def init_tiles(self, filename):
        """
        Read tile definitions from a file and create the initial set of tiles.
        Each line in the file should have: letter,point_value,quantity
        
        Args:
            filename: Path to tile definition file
        """
        global alphabet
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line_info = line.split(',')
                alphabet.append(line_info[0])
                for i in range(int(line_info[2])):
                    self.add_tile(Tile(line_info[0], int(line_info[1])))

    def add_tile(self, tile):
        """
        Add a tile to the pouch.
        
        Args:
            tile: Tile object to add
        """
        self.tiles.append(tile)

    def draw_tile(self):
        """
        Draw a random tile from the pouch.
        
        Returns:
            A random Tile object, or None if the pouch is empty
        """
        if len(self.tiles) == 0:
            return None
        index = random.randint(0, len(self.tiles) - 1)
        tile = self.tiles[index]
        self.tiles.pop(index)
        return tile
    
    def tiles_amount(self):
        """
        Get the number of tiles remaining in the pouch.
        
        Returns:
            Number of tiles
        """
        return len(self.tiles)


class Player:
    """
    Represents a player in the Scrabble game.
    Contains the player's rack and score.
    """
    def __init__(self) -> None:
        """Initialize a new player with an empty rack and zero score."""
        self.rack = Rack()
        self.score = 0
        
    def draw_tile(self, pouch):
        """
        Draw a tile from the pouch and add it to the player's rack.
        
        Args:
            pouch: Pouch object to draw from
        """
        self.rack.add_tile(pouch.draw_tile())


class Rack:
    """
    Represents a player's tile rack in the Scrabble game.
    Holds up to 7 tiles.
    """
    def __init__(self) -> None:
        """Initialize an empty rack with 7 slots."""
        self.tiles = [None] * 7

    def remove_played_tiles(self):
        """Remove all tiles marked as drafted from the rack."""
        played_indices = []
        # First find which tiles were actually played
        for i, tile in enumerate(self.tiles):
            if tile is not None and tile.draft:
                played_indices.append(i)
        
        # Then remove only those tiles that were played
        for i in played_indices:
            self.tiles[i] = None

    def fill_empty_tiles(self, pouch):
        """
        Fill empty slots in the rack with tiles from the pouch.
        
        Args:
            pouch: Pouch object to draw tiles from
            
        Returns:
            True if all empty slots were filled, False if the pouch ran out of tiles
        """
        for i, tile in enumerate(self.tiles):
            if tile is None:
                drawed_tile = pouch.draw_tile()
                if drawed_tile is not None:
                    self.tiles[i] = drawed_tile
                else:
                    return False
        return True

    def add_tile(self, tile, pos=-1):
        """
        Add a tile to the rack.
        
        Args:
            tile: Tile object to add
            pos: Position in the rack (0-6), or -1 to place in the first empty slot
        """
        if pos == -1:
            for i in range(7):
                if self.tiles[i] is None:
                    pos = i
                    break
        self.tiles[pos] = tile

    def tiles_amount(self):
        """
        Get the number of tiles currently in the rack.
        
        Returns:
            Number of tiles
        """
        amount = 0
        for tile in self.tiles:
            if tile is not None:
                amount += 1
        return amount