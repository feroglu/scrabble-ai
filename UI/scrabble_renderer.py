from Game.scrabble_objects import *
from Game.scrabble_game import *

import pygame as p
import pygame_menu as pm
import sys

# Window dimensions
WINDOW_HEIGHT = 830
WINDOW_WIDTH = 1280

# Board dimensions
BOARD_WIDTH = BOARD_HEIGHT = 750
DIMENSION = 15
LINE_WIDTH = 2
MAX_FPS = 30
SQ_SIZE = BOARD_WIDTH // DIMENSION

# Color definitions
BACKGROUND_COLOR = (240, 230, 220)  # Warmer background color
BOARD_COLOR = (235, 225, 205)  # Board background
BOARD_LINES_COLOR = (150, 120, 100)  # Board grid lines
TEXT_COLOR = (50, 40, 30)  # Dark brown text
TILE_COLOR = (250, 240, 210)  # Cream colored tiles
TILE_BORDER_COLOR = (150, 120, 100)  # Tile border
DRAFT_TILE_COLOR = (240, 230, 180)  # Brighter color for draft tiles
BUTTON_COLOR = (160, 120, 90)  # Brown for buttons
BUTTON_HOVER_COLOR = (180, 140, 110)  # Button hover color
BUTTON_TEXT_COLOR = (250, 245, 235)  # Button text
CONSOLE_COLOR = (60, 50, 40)  # Console background
CONSOLE_TEXT_COLOR = (250, 245, 235)  # Console text
AI_TITLE_COLOR = (220, 180, 140)  # AI başlık rengi (daha açık kahverengi)

# Multiplier colors
DL_COLOR = (170, 210, 230)  # Light blue - Double Letter
TL_COLOR = (100, 160, 210)  # Dark blue - Triple Letter
DW_COLOR = (230, 180, 180)  # Light red - Double Word
TW_COLOR = (210, 120, 120)  # Dark red - Triple Word
CENTER_COLOR = (220, 180, 170)  # Center square color


class Renderer:
    """
    Handles the graphical rendering of the Scrabble game.
    Manages UI interactions and display of game elements.
    """
    def __init__(self, gamestate, gameengine):
        """
        Initialize the renderer.
        
        Args:
            gamestate: The current game state
            gameengine: The game engine that handles game logic
        """
        self.gamestate = gamestate
        self.gameengine = gameengine
        self.swap_mode = False
        
    def handle_play_button(self):
        """Handle clicking the Play button."""
        print("Play clicked.")
        if not self.swap_mode:
            self.gameengine.play_draft()

    def handle_swap_button(self):
        """
        Handle clicking the Swap button.
        Toggles swap mode or executes a swap operation.
        """
        if not self.swap_mode:
            # Enter swap mode only if no tiles are already drafted
            is_able_to_swap = True
            for tile in self.gamestate.player_1.rack.tiles:
                if tile is not None and tile.draft:
                    is_able_to_swap = False
                    break
            if is_able_to_swap:
                self.swap_mode = not self.swap_mode
        else:
            # Execute the swap and exit swap mode if successful
            if self.gameengine.swap_draft():
                self.swap_mode = not self.swap_mode
                
    def handle_exit_button(self):
        """Handle clicking the Exit button."""
        print("Exit clicked.")
        p.quit()
        sys.exit()

    def handle_ai_play_button(self):
        """Handle clicking the AI Play button."""
        self.gameengine.ai_make_move()

    def handle_autoplay_button(self):
        """Toggle AI autoplay mode."""
        self.gameengine.autoplay = not self.gameengine.autoplay

    def on_change(self, option_item):
        """
        Handle selection change in the AI moves dropdown.
        
        Args:
            option_item: The selected item
        """
        # Clear any existing drafted tiles
        self.gameengine.clear_draft()
        
        # Set the selected move as draft
        for cell, tile in self.gameengine.ai_possible_moves[option_item[1]].items():
            cell.tile = tile
            tile.draft = True

    def handle_play_selection_button(self):
        """Play the currently selected AI move."""
        drop_down_widget = self.ai_possible_moves_sec.get_widget('poss_moves')
        _, selected_idx = drop_down_widget.get_value()

        if selected_idx != -1:
            self.gameengine.play_option(selected_idx)
        
        # Reset the dropdown
        drop_down_widget.reset_value()
        drop_down_widget.update_items([])

    def init_pymenus(self):
        """Initialize pygame-menu UI elements."""
        # Create a common theme for all menus
        theme = pm.Theme(
            background_color=pm.themes.TRANSPARENT_COLOR,
            title=False,
            widget_font=pm.font.FONT_FIRACODE,
            widget_font_color=BUTTON_TEXT_COLOR,
            widget_selection_effect=pm.widgets.NoneSelection()
        )
        
        # AI Algorithm selector theme (daha belirgin)
        algo_theme = pm.Theme(
            background_color=(90, 70, 60),  # Koyu kahverengi arka plan
            title=False,
            widget_font=pm.font.FONT_FIRACODE,
            widget_font_color=(250, 245, 235),  # Açık renkli yazı
            widget_selection_effect=pm.widgets.NoneSelection()
        )

        # Player action buttons (Play, Swap, Exit)
        self.player_btn_sec = pm.Menu('', 400, 40, theme=theme, rows=1, columns=3, position=(800, 120, False))
        play_btn = self.player_btn_sec.add.button("  OYNA  ", lambda: self.handle_play_button(), 
                                                button_id="play", 
                                                background_color=BUTTON_COLOR, 
                                                font_size=20, 
                                                shadow_width=10)
        swap_btn = self.player_btn_sec.add.button(" DEĞİŞTİR ", lambda: self.handle_swap_button(), 
                                                button_id="swap", 
                                                background_color=BUTTON_COLOR, 
                                                font_size=20, 
                                                shadow_width=10)
        exit_btn = self.player_btn_sec.add.button("  ÇIKIŞ  ", lambda: self.handle_exit_button(), 
                                                button_id="exit", 
                                                background_color=(190, 80, 70),  # Kırmızımsı 
                                                font_size=20, 
                                                shadow_width=10)
        play_btn.resize(120, 40, True)
        swap_btn.resize(120, 40, True)
        exit_btn.resize(120, 40, True)
        
        # AI control buttons (AI Play, Autoplay)
        self.ai_opt_btn_sec = pm.Menu('', 300, 40, theme=theme, rows=1, columns=2, position=(850, 230, False))
        ai_play_btn = self.ai_opt_btn_sec.add.button("AI OYNA", lambda: self.handle_ai_play_button(), 
                                                    button_id="ai_play", 
                                                    background_color=BUTTON_COLOR, 
                                                    font_size=20, 
                                                    shadow_width=10)
        autoplay_btn = self.ai_opt_btn_sec.add.button("OTOMATİK", lambda: self.handle_autoplay_button(), 
                                                    button_id="autoplay", 
                                                    background_color=BUTTON_COLOR, 
                                                    font_size=20, 
                                                    shadow_width=10)
        ai_play_btn.resize(120, 40, True)
        autoplay_btn.resize(120, 40, True)
        
        # AI possible moves section
        self.ai_possible_moves_sec = pm.Menu('', 400, 230, theme=theme, rows=3, columns=1, position=(800, 430, False))

        # Dropdown for possible AI moves
        self.ai_possible_moves_sec.add.dropselect(
            title='',
            items=['---'],
            onchange=self.on_change,
            dropselect_id='poss_moves',
            font_size=16,
            padding=0,
            placeholder='Select one',
            selection_box_height=5,
            selection_box_inflate=(0, 20),
            selection_box_margin=0,
            selection_box_text_margin=10,
            selection_box_width=400,
            selection_option_font_size=20,
            shadow_width=20,
            margin=(0, 10)
        )
        
        # Console surface for logs
        console_surf = p.Surface((375, 120))
        self.ai_possible_moves_sec.add.surface(console_surf)

        # Button to play the selected move
        selected_play_btn = self.ai_possible_moves_sec.add.button("SEÇİMİ OYNA", 
                                                                lambda: self.handle_play_selection_button(), 
                                                                button_id="selected_play", 
                                                                background_color=BUTTON_COLOR, 
                                                                font_size=20, 
                                                                shadow_width=10)
        selected_play_btn.resize(120, 40, True)
        
        # AI Algorithm selector
        self.ai_algorithm_sec = pm.Menu('', 450, 80, theme=algo_theme, rows=1, columns=1, position=(780, 700, False))
        algorithm_selector = self.ai_algorithm_sec.add.selector(
            title='AI ALGORİTMASI:',
            items=[('Standart', 'standard'), ('Minimax', 'minimax'), ('Harf Analizi', 'letter_analysis')],
            onchange=self.change_ai_algorithm,
            selector_id='algorithm_selector',
            font_size=20
        )
        algorithm_selector.set_background_color((120, 90, 70))  # Buton arka plan 

    def render_game(self, surf):
        """
        Render the entire game interface.
        
        Args:
            surf: Surface to render on
        """
        # Fill background
        surf_rect = surf.get_rect()
        surf.fill(BACKGROUND_COLOR)
        
        # Render game board
        gameboard_surf = p.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        self.render_board(self.gamestate.board, gameboard_surf)
        surf.blit(gameboard_surf, (0, 0))
        
        # Render player scores
        font_12 = p.font.Font('freesansbold.ttf', 12)
        rendered_text = font_12.render("OYUNCU - {}".format(self.gamestate.player_1.score), True, TEXT_COLOR)
        surf.blit(rendered_text, (760, 10))
        
        rendered_text = font_12.render("{} - AI".format(self.gamestate.player_2.score), True, TEXT_COLOR)
        surf.blit(rendered_text, (1200, 10))
        
        # Render player rack section
        font_16 = p.font.Font('freesansbold.ttf', 16)
        rendered_text = font_16.render("OYUNCU RAFI", True, TEXT_COLOR)
        surf.blit(rendered_text, (940, 20))

        rack1_surf = p.Surface((SQ_SIZE * 7, SQ_SIZE))
        self.render_rack(self.gamestate.player_1.rack, rack1_surf)
        surf.blit(rack1_surf, (825, 50))
        
        # Update swap button color based on mode
        self.player_btn_sec.get_widget('swap').update_font({
            'color': ((0, 255, 0) if self.swap_mode else BUTTON_TEXT_COLOR)
        })
        self.player_btn_sec.draw(surf)

        # Divider line
        p.draw.line(surf, BOARD_LINES_COLOR, (BOARD_WIDTH, 190), (WINDOW_WIDTH, 190), 2)

        # Render AI section
        rendered_text = font_16.render("AI", True, TEXT_COLOR)
        surf.blit(rendered_text, (990, 200))

        # Update autoplay button color based on status
        self.ai_opt_btn_sec.get_widget('autoplay').update_font({
            'color': ((0, 255, 0) if self.gameengine.autoplay else BUTTON_TEXT_COLOR)
        })
        self.ai_opt_btn_sec.draw(surf)

        # Divider line
        p.draw.line(surf, BOARD_LINES_COLOR, (BOARD_WIDTH, 290), (WINDOW_WIDTH, 290), 2)
        
        # Render AI rack
        rendered_text = font_16.render("AI RAFI", True, TEXT_COLOR)
        surf.blit(rendered_text, (965, 310))

        rack2_surf = p.Surface((SQ_SIZE * 7, SQ_SIZE))
        self.render_rack(self.gamestate.player_2.rack, rack2_surf)
        surf.blit(rack2_surf, (825, 340))

        # Render possible moves section
        rendered_text = font_16.render("OLASI HAMLELER", True, TEXT_COLOR)
        surf.blit(rendered_text, (925, 410))
            
        # Update possible moves dropdown if new moves are available
        if len(self.gameengine.ai_possible_move_ids) > 0:
            self.ai_possible_moves_sec.get_widget('poss_moves').update_items(self.gameengine.ai_possible_move_ids)
            self.gameengine.ai_possible_move_ids.clear()
        
        self.ai_possible_moves_sec.draw(surf)
        
        # Render log messages
        line_y = 510
        for line in self.gameengine.logs[-8:]:  # Show only the last 8 lines
            rendered_text = font_12.render(line, True, (255, 255, 255))
            surf.blit(rendered_text, (820, line_y))
            line_y += 15
        
        # Divider line - AI algoritması seçimi için
        p.draw.line(surf, BOARD_LINES_COLOR, (BOARD_WIDTH, 670), (WINDOW_WIDTH, 670), 2)
        
        # Render AI Algorithm selector
        font_18 = p.font.Font('freesansbold.ttf', 20)
        rendered_text = font_18.render("AI ALGORİTMA SEÇİMİ", True, AI_TITLE_COLOR)
        text_rect = rendered_text.get_rect(center=(950, 685))
        surf.blit(rendered_text, text_rect)
        self.ai_algorithm_sec.draw(surf) 

    def change_ai_algorithm(self, value, algorithm):
        """
        AI algoritmasını değiştir
        
        Args:
            value: Seçici değeri
            algorithm: Seçilen algoritma
        """
        self.gameengine.ai_algorithm = algorithm
        print(f"AI Algoritması değiştirildi: {value[0]}")
        
    def render_board(self, board, surf):
        """
        Render the game board.
        
        Args:
            board: The game board to render
            surf: Surface to render on
        """
        # Fill board background
        surf.fill(BOARD_COLOR)
        
        # Draw board squares
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                # Calculate square position
                sq_rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                
                # Cell center multiplier
                celltype = board.board[r][c].celltype
                
                # Color based on cell type
                if celltype == CellType.CENTER:
                    p.draw.rect(surf, CENTER_COLOR, sq_rect)
                elif celltype == CellType.DL:
                    p.draw.rect(surf, DL_COLOR, sq_rect)
                elif celltype == CellType.TL:
                    p.draw.rect(surf, TL_COLOR, sq_rect)
                elif celltype == CellType.DW:
                    p.draw.rect(surf, DW_COLOR, sq_rect)
                elif celltype == CellType.TW:
                    p.draw.rect(surf, TW_COLOR, sq_rect)
                else:
                    p.draw.rect(surf, BOARD_COLOR, sq_rect)
                
                # Draw cell borders
                p.draw.rect(surf, BOARD_LINES_COLOR, sq_rect, 1)
                
                # Draw special cell text
                cell_label = ""
                if celltype == CellType.DL:
                    cell_label = "DL"
                elif celltype == CellType.TL:
                    cell_label = "TL"
                elif celltype == CellType.DW:
                    cell_label = "DW"
                elif celltype == CellType.TW:
                    cell_label = "TW"
                elif celltype == CellType.CENTER:
                    cell_label = "★"
                
                if cell_label:
                    font = p.font.Font('freesansbold.ttf', 12)
                    text = font.render(cell_label, True, TEXT_COLOR)
                    text_rect = text.get_rect(center=sq_rect.center)
                    surf.blit(text, text_rect)
                
                # Draw tile on the cell if present
                if board.board[r][c].tile:
                    self.render_tile(board.board[r][c].tile, surf, (c * SQ_SIZE, r * SQ_SIZE))
    
    def render_rack(self, rack, surf):
        """
        Render the player's tile rack.
        
        Args:
            rack: The tile rack to render
            surf: Surface to render on
        """
        # Fill rack background
        surf.fill(BOARD_COLOR)
        
        # Draw tiles in the rack
        for i, tile in enumerate(rack.tiles):
            # Draw empty rack position
            p.draw.rect(surf, BOARD_COLOR, p.Rect(i * SQ_SIZE, 0, SQ_SIZE, SQ_SIZE))
            p.draw.rect(surf, BOARD_LINES_COLOR, p.Rect(i * SQ_SIZE, 0, SQ_SIZE, SQ_SIZE), 1)
            
            # Render tile if present
            if tile:
                self.render_tile(tile, surf, (i * SQ_SIZE, 0))
                
    def render_tile(self, tile, surf, pos=(0, 0)):
        """
        Render a single Scrabble tile.
        
        Args:
            tile: The tile to render
            surf: Surface to render on
            pos: Position (x, y) to draw at
        """
        # Set tile background color based on draft status
        bg_color = DRAFT_TILE_COLOR if tile.draft else TILE_COLOR
        
        # Draw tile background
        rect = p.Rect(pos[0], pos[1], SQ_SIZE, SQ_SIZE)
        p.draw.rect(surf, bg_color, rect)
        p.draw.rect(surf, TILE_BORDER_COLOR, rect, 2)
        
        # Draw letter
        font_size = 24 if len(tile.letter) == 1 else 18
        font = p.font.Font('freesansbold.ttf', font_size)
        text = font.render(tile.letter, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(pos[0] + SQ_SIZE // 2, pos[1] + SQ_SIZE // 2 - 5))
        surf.blit(text, text_rect)
        
        # Draw point value
        font = p.font.Font('freesansbold.ttf', 12)
        text = font.render(str(tile.point), True, TEXT_COLOR)
        text_rect = text.get_rect(bottomright=(pos[0] + SQ_SIZE - 5, pos[1] + SQ_SIZE - 3))
        surf.blit(text, text_rect)
        
    def board_col_detect(self, x, y):
        """
        Detect if the mouse is over a board position.
        
        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            
        Returns:
            Tuple (is_collision, (row, col))
        """
        # Check if coordinates are on the board
        if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
            return False, (-1, -1)
            
        # Calculate board position
        board_col = x // SQ_SIZE
        board_row = y // SQ_SIZE
        
        return True, (board_row, board_col)
    
    def rack_col_detect(self, x, y):
        """
        Detect if the mouse is over a rack position.
        
        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            
        Returns:
            Tuple (is_collision, rack_idx)
        """
        # Check if coordinates are in the rack area
        rack_x_start = 825
        rack_y = 50
        
        if x < rack_x_start or x >= rack_x_start + 7 * SQ_SIZE or y < rack_y or y >= rack_y + SQ_SIZE:
            return False, -1
            
        # Calculate rack position
        rack_pos = (x - rack_x_start) // SQ_SIZE
        
        return True, rack_pos
    
    def init_location_rects(self):
        """Initialize rectangles for board locations."""
        pass  # This function is not needed but kept for compatibility 