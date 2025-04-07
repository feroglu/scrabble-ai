from YapayZeka.trie import *
from Oyun.scrabble_nesneler import alphabet


class WordFinder:
    """
    Class that finds valid words that can be played on a Scrabble board.
    Uses a trie data structure for efficient word lookup.
    """
    def __init__(self, word_list_file, board):
        self.trie = Trie(word_list_file)
        self.board_obj = board
        self.board = board.board
        self.rack = None
        self.cross_suitable_letters = None
        self.is_horizontal = True
        self.ai_possible_moves = list()

    def find_anchors(self):
        """Find all anchor positions on the board where new tiles can be placed."""
        anchors = []
        for pos in self.board_obj.all_positions():
            is_empty = self.board_obj.is_empty(pos)
            neighbor_filled = (self.board_obj.has_left(pos) or 
                              self.board_obj.has_right(pos) or 
                              self.board_obj.has_up(pos) or 
                              self.board_obj.has_down(pos))

            if is_empty and neighbor_filled:
                anchors.append(pos)
        return anchors
    
    def legal_move(self, move_record):
        """Add a valid move to the list of possible moves."""
        self.ai_possible_moves.append(move_record.copy())

    def extend_after(self, partial_word, cur_node, next_pos, move_record, anchor_filled):
        """
        Recursively extend a word after an anchor point.
        
        Args:
            partial_word: The word being built so far
            cur_node: Current node in the trie
            next_pos: Next position to consider
            move_record: Dictionary mapping board positions to tiles
            anchor_filled: Whether the anchor position has been filled
        """
        # If we've reached the end of a valid word after filling an anchor, record the move
        if not(self.board_obj.is_inbounds(next_pos) and not self.board_obj.is_empty(next_pos)) and cur_node.is_word and anchor_filled:
            self.legal_move(move_record)
            
        if self.board_obj.is_inbounds(next_pos):
            if self.board_obj.is_empty(next_pos):
                # Try each tile in the rack
                for i, tile in enumerate(self.rack.tiles):
                    if (tile is not None and 
                        tile.letter in cur_node.children.keys() and 
                        tile.letter in self.cross_suitable_letters[next_pos]):
                        
                        # Place the tile temporarily
                        self.rack.tiles[i] = None
                        move_record[self.board_obj.get_pos(next_pos)] = tile
                        
                        # Recurse
                        self.extend_after(
                            partial_word + tile.letter,
                            cur_node.children[tile.letter],
                            self.board_obj.after(next_pos, self.is_horizontal),
                            move_record,
                            True
                        )
                        
                        # Backtrack
                        move_record.popitem()  # Python version > 3.7 is REQUIRED just for this line
                        self.rack.tiles[i] = tile
            else:
                # Extend through an existing tile
                existing_letter = self.board_obj.get_pos(next_pos).tile.letter
                if existing_letter in cur_node.children.keys():
                    self.extend_after(
                        partial_word + existing_letter,
                        cur_node.children[existing_letter],
                        self.board_obj.after(next_pos, self.is_horizontal),
                        move_record,
                        True
                    )

    def before_part(self, partial_word, cur_node, anchor_pos, move_record, limit):
        """
        Build the part of the word before the anchor position.
        
        Args:
            partial_word: The word being built so far
            cur_node: Current node in the trie
            anchor_pos: The anchor position
            move_record: Dictionary mapping board positions to tiles
            limit: Maximum number of tiles that can be placed before the anchor
        """
        # Try extending after the anchor without placing anything before
        self.extend_after(partial_word, cur_node, anchor_pos, move_record, False)
        
        if limit <= 0:
            return
            
        # Try each tile in the rack
        for i, tile in enumerate(self.rack.tiles):
            if tile is not None and tile.letter in cur_node.children.keys():
                # Place the tile temporarily
                self.rack.tiles[i] = None
                move_record[self.board_obj.get_pos(anchor_pos)] = tile
                
                # Shift positions backward
                records_before_shift = move_record.copy()
                move_record.clear()
                for cell, cell_tile in records_before_shift.items():
                    move_record[self.board_obj.get_pos(self.board_obj.before(cell.position, self.is_horizontal))] = cell_tile

                # Recurse
                self.before_part(
                    partial_word + tile.letter,
                    cur_node.children[tile.letter],
                    anchor_pos,
                    move_record,
                    limit - 1
                )

                # Backtrack and shift positions forward
                move_record.popitem()
                records_before_shift = move_record.copy()
                move_record.clear()
                for cell, cell_tile in records_before_shift.items():
                    move_record[self.board_obj.get_pos(self.board_obj.after(cell.position, self.is_horizontal))] = cell_tile

                self.rack.tiles[i] = tile
    
    def find_all_plays(self, rack):
        """
        Find all valid plays for the given rack.
        
        Args:
            rack: The player's tile rack
        
        Returns:
            A list of all possible moves
        """
        self.rack = rack
        self.ai_possible_moves.clear()
        
        # Try both horizontal and vertical placements
        for self.is_horizontal in [True, False]:
            move_record = dict()
            self.cross_suitable_letters = self.get_cross_suitable_letters()
            anchors = self.find_anchors()
            
            # Special case: first move must use center square
            if self.board_obj.is_empty((7, 7)):
                anchors.append((7, 7))
                
            for anchor_pos in anchors:
                if self.board_obj.has_before(anchor_pos, self.is_horizontal):
                    # There's an existing tile before this anchor
                    # Build the existing word prefix
                    seek_pos = self.board_obj.before(anchor_pos, self.is_horizontal)
                    partial_word = self.board_obj.get_pos(seek_pos).tile.letter
                    
                    while self.board_obj.has_before(seek_pos, self.is_horizontal):
                        seek_pos = self.board_obj.before(seek_pos, self.is_horizontal)
                        partial_word = self.board_obj.get_pos(seek_pos).tile.letter + partial_word
                    
                    # Try to extend after the existing word
                    partial_word_node = self.trie.lookup_string(partial_word)
                    if partial_word_node is not None:
                        self.extend_after(partial_word, partial_word_node, anchor_pos, move_record, False)
                else:
                    # No existing tiles before this anchor
                    # Calculate how many tiles we can place before
                    before_limit = 0
                    seek_pos = anchor_pos
                    
                    # We can prevent merging while extending to the before since there 
                    # will be an extension to the after of those anchors anyway
                    while (self.board_obj.is_inbounds(self.board_obj.before(seek_pos, self.is_horizontal)) and
                           self.board_obj.is_empty(self.board_obj.before(seek_pos, self.is_horizontal)) and
                           self.board_obj.before(seek_pos, self.is_horizontal) not in anchors):
                        before_limit += 1
                        seek_pos = self.board_obj.before(seek_pos, self.is_horizontal)
                    
                    # Try to place tiles before and after the anchor
                    self.before_part("", self.trie.root, anchor_pos, move_record, before_limit)
                    
        return self.ai_possible_moves.copy()

    def get_cross_suitable_letters(self):
        """
        For each empty cell, determine which letters would form valid words
        in the perpendicular direction.
        
        Returns:
            A dictionary mapping positions to lists of valid letters
        """
        check_results = dict()
        
        for pos in self.board_obj.all_positions():
            if not self.board_obj.is_empty(pos):
                continue
                
            # Get the letters before this position (perpendicular to current direction)
            letters_before = ""
            seek_pos = pos
            while self.board_obj.has_before(seek_pos, not self.is_horizontal):
                seek_pos = self.board_obj.before(seek_pos, not self.is_horizontal)
                letters_before = self.board_obj.get_pos(seek_pos).tile.letter + letters_before
            
            # Get the letters after this position (perpendicular to current direction)
            letters_after = ""
            seek_pos = pos
            while self.board_obj.has_after(seek_pos, not self.is_horizontal):
                seek_pos = self.board_obj.after(seek_pos, not self.is_horizontal)
                letters_after = letters_after + self.board_obj.get_pos(seek_pos).tile.letter
            
            # If there are no perpendicular constraints, any letter is valid
            if len(letters_before) + len(letters_after) == 0:
                suitable_letters = alphabet.copy()
            else:
                # Otherwise, check which letters would form valid cross-words
                suitable_letters = []
                for letter in alphabet:
                    word = letters_before + letter + letters_after
                    if self.trie.is_word(word):
                        suitable_letters.append(letter)
            
            check_results[pos] = suitable_letters
            
        return check_results