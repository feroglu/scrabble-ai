from Oyun.scrabble_nesneler import *
from Oyun.scrabble_motor import *

import pygame as p
import pygame_menu as pm

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
        self.last_log_count = 0  # Son log sayısını takip et
        self.console_scroll_pos = 0  # Kaydırma pozisyonu başlangıçta 0
        
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

    def handle_ai_play_button(self):
        """Handle clicking the AI Play button."""
        self.gameengine.ai_make_move()

    def handle_autoplay_button(self):
        """Toggle AI autoplay mode."""
        self.gameengine.autoplay = not self.gameengine.autoplay

    def handle_end_game_button(self):
        """Oyunu manuel olarak sonlandırır ve sonuç ekranını gösterir."""
        print("Oyun bitti - Sonuçlar:")
        
        # Sonuçları loglara ekle
        self.gameengine.logs.append("")
        self.gameengine.logs.append("------ OYUN SONUÇLARI ------")
        self.gameengine.logs.append(f"OYUNCU PUANI: {self.gamestate.player_1.score}")
        self.gameengine.logs.append(f"AI PUANI: {self.gamestate.player_2.score}")
        
        if self.gamestate.player_1.score > self.gamestate.player_2.score:
            self.gameengine.logs.append("TEBRİKLER! KAZANDINIZ!")
        elif self.gamestate.player_2.score > self.gamestate.player_1.score:
            self.gameengine.logs.append("AI KAZANDI!")
        else:
            self.gameengine.logs.append("BERABERE!")
            
        self.gameengine.logs.append("")
        self.gameengine.logs.append("Çıkmak için pencere çarpısına basın.")
        
        # Konsolu güncelle ve kaydırma pozisyonunu sıfırla (en yeni mesajları göster)
        self.console_scroll_pos = 0 
        self.update_console()
        
        # Oyunu bitti olarak işaretle, ama kapatma
        self.gamestate.game_ended = True

    def on_change(self, option_item):
        """
        Eski olası hamleler seçimi için yöntem.
        Artık kullanılmıyor, fakat kod uyumluluğu için korundu.
        """
        pass

    def handle_play_selection_button(self):
        """
        Eski olası hamleler butonunu işleme yöntemi.
        Artık kullanılmıyor, fakat kod uyumluluğu için korundu.
        """
        pass

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

        # Player action buttons (Play, Swap)
        self.player_btn_sec = pm.Menu('', 300, 40, theme=theme, rows=1, columns=2, position=(850, 120, False))
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
        play_btn.resize(120, 40, True)
        swap_btn.resize(120, 40, True)
        
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
        
        # Konsol bölümü (olası hamleler bölümü görünmeyecek şekilde)
        self.ai_possible_moves_sec = pm.Menu('', 400, 320, theme=theme, rows=2, columns=1, position=(800, 380, False))
        
        # Console surface for logs
        self.console_surf = p.Surface((375, 250))
        self.console_surf.fill(CONSOLE_COLOR)
        self.console_scroll_pos = 0  # Kaydırma pozisyonu
        self.log_font = p.font.SysFont("consolas", 12, True, False)
        self.console_widget = self.ai_possible_moves_sec.add.surface(self.console_surf, surface_id="console_surface")
        
        # Orta nokta hesaplama
        center_x = BOARD_WIDTH + (WINDOW_WIDTH - BOARD_WIDTH) // 2
        
        # Oyunu Bitir butonu - sol alt köşe
        self.end_game_sec = pm.Menu('', 150, 50, theme=theme, rows=1, columns=1, position=(20, 780, False))
        end_game_btn = self.end_game_sec.add.button("OYUNU BİTİR", 
                                               lambda: self.handle_end_game_button(), 
                                               button_id="end_game", 
                                               background_color=(200, 50, 50),  # Daha canlı kırmızı
                                               font_size=18, 
                                               shadow_width=10,
                                               font_color=(255, 255, 255))  # Beyaz yazı
        end_game_btn.resize(140, 40, True)
        
        # AI Algorithm selector
        self.ai_algorithm_sec = pm.Menu('', 550, 50, theme=theme, rows=1, columns=2, position=(center_x - 300, 740, False))
        algorithm_selector = self.ai_algorithm_sec.add.selector(
            title='AI ALGORİTMASI:',
            items=[('Standart', 'standard'), ('Minimax', 'minimax'), ('Monte Carlo', 'monte_carlo'), ('Harf Analizi', 'letter_analysis')],
            onchange=self.change_ai_algorithm,
            selector_id='algorithm_selector',
            font_size=18
        )
        algorithm_selector.set_background_color((120, 90, 70))  # Buton arka plan
        
        # Button to show algorithm stats
        stats_button = self.ai_algorithm_sec.add.button(" İSTATİSTİKLER ", 
                                                      lambda: self.show_algorithm_stats(), 
                                                      button_id="stats_button", 
                                                      background_color=BUTTON_COLOR, 
                                                      font_size=16, 
                                                      shadow_width=10)
        stats_button.resize(120, 30, True)

    def rack_col_detect(self, x, y):
        """
        Detect if the mouse is over a rack position.
        
        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            
        Returns:
            Tuple (is_collision, position_index)
        """
        for i in range(7):
            if self.rack_rects[i].collidepoint(x, y):
                return True, i
        return False, -1
            
    def board_col_detect(self, x, y):
        """
        Detect if the mouse is over a board position.
        
        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            
        Returns:
            Tuple (is_collision, (row, col))
        """
        for i in range(15):
            for j in range(15):
                if self.board_rects[i][j].collidepoint(x, y):
                    return True, (i, j)
        return False, (-1, -1)

    def init_location_rects(self):
        """Initialize rectangles for board and rack positions."""
        # Rack rectangles
        self.rack_rects = []
        for i in range(7):
            self.rack_rects.append(p.Rect(825 + i * SQ_SIZE, 50, SQ_SIZE, SQ_SIZE))

        # Board rectangles
        self.board_rects = []
        for i in range(15):
            row = []
            for j in range(15):
                start_pos_y = i * SQ_SIZE
                start_pos_x = j * SQ_SIZE
                row.append(p.Rect(start_pos_x, start_pos_y, SQ_SIZE, SQ_SIZE))
            self.board_rects.append(row)

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
        
        # Oyun bittiğinde daha büyük sonuç göster
        if self.gamestate.game_ended:
            font_24 = p.font.Font('freesansbold.ttf', 24)
            
            # Sonuç metni
            result_text = "BERABERE!"
            text_color = (255, 215, 0)  # Altın rengi
            
            if self.gamestate.player_1.score > self.gamestate.player_2.score:
                result_text = "TEBRİKLER! KAZANDINIZ!"
                text_color = (50, 205, 50)  # Yeşil
            elif self.gamestate.player_2.score > self.gamestate.player_1.score:
                result_text = "AI KAZANDI!"
                text_color = (220, 20, 60)  # Kırmızı
                
            # Puan metni
            score_text = f"OYUNCU: {self.gamestate.player_1.score}  -  AI: {self.gamestate.player_2.score}"
            
            # Yarı saydam arka plan dikdörtgeni çiz
            result_bg_rect = p.Rect(0, 300, BOARD_WIDTH, 150)
            bg_surface = p.Surface((result_bg_rect.width, result_bg_rect.height), p.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Yarı saydam siyah
            surf.blit(bg_surface, result_bg_rect)
            
            # Sonuç metnini çiz
            result_rendered = font_24.render(result_text, True, text_color)
            result_rect = result_rendered.get_rect(center=(BOARD_WIDTH//2, 340))
            surf.blit(result_rendered, result_rect)
            
            # Puan metnini çiz
            score_rendered = font_24.render(score_text, True, (255, 255, 255))
            score_rect = score_rendered.get_rect(center=(BOARD_WIDTH//2, 380))
            surf.blit(score_rendered, score_rect)
            
            # Çıkış talimatı
            exit_text = "Çıkmak için pencere çarpısına basın."
            exit_rendered = font_12.render(exit_text, True, (200, 200, 200))
            exit_rect = exit_rendered.get_rect(center=(BOARD_WIDTH//2, 420))
            surf.blit(exit_rendered, exit_rect)
        
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

        # Konsol başlığı
        font_16 = p.font.Font('freesansbold.ttf', 16)
        rendered_text = font_16.render("KONSOL", True, TEXT_COLOR)
        surf.blit(rendered_text, (965, 395))
        
        # Konsolu güncelle
        self.update_console()
            
        # Update possible moves dropdown if new moves are available
        if len(self.gameengine.ai_possible_move_ids) > 0:
            self.ai_possible_moves_sec.get_widget('poss_moves').update_items(self.gameengine.ai_possible_move_ids)
            self.gameengine.ai_possible_move_ids.clear()
        
        self.ai_possible_moves_sec.draw(surf)
        
        # Render log messages
        # Artık konsol widget içinde çiziliyor, burada gerek yok
        
        # Divider line - AI algoritması seçimi için
        p.draw.line(surf, BOARD_LINES_COLOR, (BOARD_WIDTH, 670), (WINDOW_WIDTH, 670), 2)
        
        # Render AI Algorithm selector (başlık ve seçici)
        font_18 = p.font.Font('freesansbold.ttf', 18)
        rendered_text = font_18.render("AI ALGORİTMA SEÇİMİ", True, (220, 180, 140))  # AI başlık rengi
        text_rect = rendered_text.get_rect(center=(950, 720))
        surf.blit(rendered_text, text_rect)
        self.ai_algorithm_sec.draw(surf)
        
        # Render the exit button
        self.end_game_sec.draw(surf)

    def render_board(self, board, surf):
        """
        Render the game board.
        
        Args:
            board: Board object to render
            surf: Surface to render on
        """
        # Render each cell
        for i in range(DIMENSION):
            for j in range(DIMENSION):
                start_pos_y = i * SQ_SIZE
                start_pos_x = j * SQ_SIZE
                cell_surf = p.Surface((SQ_SIZE, SQ_SIZE))
                self.render_cell(board.board[i][j], cell_surf)
                surf.blit(cell_surf, (start_pos_x, start_pos_y))
        
        # Draw grid lines
        for i in range(DIMENSION):
            start_pos = i * SQ_SIZE
            p.draw.line(surf, BOARD_LINES_COLOR, (start_pos, 0), (start_pos, BOARD_HEIGHT), LINE_WIDTH)
            p.draw.line(surf, BOARD_LINES_COLOR, (0, start_pos), (BOARD_WIDTH, start_pos), LINE_WIDTH)

        # Draw border lines
        p.draw.line(surf, BOARD_LINES_COLOR, (DIMENSION * SQ_SIZE - LINE_WIDTH, 0), 
                   (DIMENSION * SQ_SIZE - LINE_WIDTH, BOARD_HEIGHT), LINE_WIDTH)
        p.draw.line(surf, BOARD_LINES_COLOR, (0, DIMENSION * SQ_SIZE - LINE_WIDTH), 
                   (BOARD_WIDTH, DIMENSION * SQ_SIZE - LINE_WIDTH), LINE_WIDTH)

    def render_cell(self, cell, surf):
        """
        Render a single board cell.
        
        Args:
            cell: Cell object to render
            surf: Surface to render on
        """
        cell_surf = surf
        cell_surf_rect = surf.get_rect()
        size = cell_surf_rect.size

        if cell.tile is not None:
            # Cell has a tile - render it
            self.render_tile(cell.tile, surf)
        elif cell.position == (7, 7):
            # Center cell - render star
            cell_surf.fill(CENTER_COLOR)
            cell_surf.blit(p.transform.scale(p.image.load("Veri/star.png"), size), cell_surf_rect)
        else:
            # Regular cell - render multiplier
            font = p.font.Font('freesansbold.ttf', 10)
            multiplier = cell.multiplier

            # Set color and text based on multiplier type
            if multiplier == 'DL':
                splitted_text = ['DOUBLE', 'LETTER', 'SCORE']
                color = DL_COLOR
            elif multiplier == 'TL':
                splitted_text = ['TRIPLE', 'LETTER', 'SCORE']
                color = TL_COLOR
            elif multiplier == 'DW':
                splitted_text = ['DOUBLE', 'WORD', 'SCORE']
                color = DW_COLOR
            elif multiplier == 'TW':
                splitted_text = ['TRIPLE', 'WORD', 'SCORE']
                color = TW_COLOR
            else:
                splitted_text = []
                color = BOARD_COLOR

            cell_surf.fill(color)

            # Render multiplier text
            font_linesize = font.get_linesize()
            offset = -1
            for t in splitted_text:
                rendered_text = font.render(t, True, TEXT_COLOR)
                rendered_text_rect = rendered_text.get_rect()
                rendered_text_rect.center = cell_surf_rect.center
                rendered_text_rect.y += offset * font_linesize
                cell_surf.blit(rendered_text, rendered_text_rect)
                offset += 1

    def render_tile(self, tile, surf):
        """
        Render a tile.
        
        Args:
            tile: Tile object to render
            surf: Surface to render on
        """
        surf_rect = surf.get_rect()
        size = surf_rect.size

        # Fill background based on draft status
        if tile.draft:
            surf.fill(DRAFT_TILE_COLOR)
        else:
            surf.fill(TILE_COLOR)

        # Render letter
        font = p.font.Font('freesansbold.ttf', 24)
        rendered_text = font.render(tile.letter, True, TEXT_COLOR)
        rendered_text_rect = rendered_text.get_rect()
        rendered_text_rect.center = surf_rect.center
        surf.blit(rendered_text, rendered_text_rect)

        # Render point value
        font = p.font.Font('freesansbold.ttf', 20)
        rendered_text = font.render(str(tile.point), True, TEXT_COLOR)
        rendered_text_rect = rendered_text.get_rect()
        rendered_text_rect.center = surf_rect.center
        rendered_text_rect.bottom = size[1]
        rendered_text_rect.right = size[0] - 3
        surf.blit(rendered_text, rendered_text_rect)

    def render_rack(self, rack, surf):
        """
        Render a tile rack.
        
        Args:
            rack: Rack object to render
            surf: Surface to render on
        """
        surf_rect = surf.get_rect()

        # Fill rack background
        p.draw.rect(surf, (128, 128, 128), surf.get_rect())
    
        # Render each tile
        for i in range(7):
            start_pos_x = SQ_SIZE * i
            if rack.tiles[i] is not None:
                rect_surf = p.Surface((SQ_SIZE, SQ_SIZE))
                self.render_tile(rack.tiles[i], rect_surf)
                
                # Make drafted tiles semi-transparent
                if rack.tiles[i].draft:
                    rect_surf.set_alpha(30)
                    
                surf.blit(rect_surf, (start_pos_x, 0))

        # Draw grid lines
        for i in range(7):
            start_pos = i * SQ_SIZE
            p.draw.line(surf, (0, 0, 0), (start_pos, 0), (start_pos, SQ_SIZE), LINE_WIDTH)
            
        p.draw.line(surf, (0, 0, 0), (7 * SQ_SIZE - LINE_WIDTH, 0), (7 * SQ_SIZE - LINE_WIDTH, SQ_SIZE), LINE_WIDTH)
        p.draw.line(surf, (0, 0, 0), surf_rect.topleft, surf_rect.topright)
        p.draw.line(surf, (0, 0, 0), 
                   (surf_rect.bottomleft[0], surf_rect.bottomleft[1] - LINE_WIDTH), 
                   (surf_rect.bottomright[0], surf_rect.bottomright[1] - LINE_WIDTH), 
                   LINE_WIDTH)

    def render_buttons(self, surf):
        """
        Render additional buttons.
        This method is currently empty but could be used to add more UI elements.
        
        Args:
            surf: Surface to render on
        """
        pass

    def change_ai_algorithm(self, value, algorithm):
        """
        AI algoritmasını değiştir
        
        Args:
            value: Seçici değeri
            algorithm: Seçilen algoritma
        """
        self.gameengine.ai_algorithm = algorithm
        print(f"AI Algoritması değiştirildi: {value[0]}")

    def show_algorithm_stats(self):
        """Display performance statistics for all AI algorithms."""
        # Get performance data
        stats = self.gameengine.get_algorithm_performance()
        
        # Format and display in console
        self.gameengine.logs.append("--- AI ALGORİTMA İSTATİSTİKLERİ ---")
        
        for algo, data in stats.items():
            # Skip if no moves made
            if data["moves"] == 0:
                continue
                
            algo_name = {
                "standard": "Standart",
                "minimax": "Minimax",
                "monte_carlo": "Monte Carlo",
                "letter_analysis": "Harf Analizi"
            }.get(algo, algo)
            
            self.gameengine.logs.append(f"{algo_name}: {data['moves']} hamle")
            self.gameengine.logs.append(f"  Ort. Puan: {data['avg_points']:.2f}")
            self.gameengine.logs.append(f"  Ort. Süre: {data['avg_time']*1000:.1f} ms")
            self.gameengine.logs.append(f"  Toplam: {data['total_points']} puan")
        
        # İstatistiklerin görünür olması için kaydırma pozisyonunu sıfırla
        # (Sıfır değeri artık en yeni mesajları gösterir)
        self.console_scroll_pos = 0

    def update_console(self):
        """Konsolu güncelleyen yardımcı fonksiyon"""
        # Konsol içeriğini güncelle
        self.console_surf.fill(CONSOLE_COLOR)
        
        # Loglarda kaç satır var
        total_logs = len(self.gameengine.logs)
        
        # Eğer log sayısı değiştiyse 
        if total_logs != self.last_log_count:
            # Yeni log eklendiğinde otomatik olarak en alttaki satırları göster
            # (Ancak kullanıcı yukarı kaydırmışsa onu rahatsız etme)
            if total_logs > self.last_log_count and self.console_scroll_pos < 5:
                self.console_scroll_pos = 0
            self.last_log_count = total_logs
        
        # Tek seferde gösterilen maksimum log sayısı
        visible_logs_max = 18
        
        # Görünür satır sayısı (rehber satırı varsa bir eksilecek)
        visible_logs = min(visible_logs_max, total_logs)
        
        # Kaydırma miktarında üst sınır: toplam log sayısı - görünür satır sayısı
        # Bu, son satırların her zaman görüntülenebilmesini sağlar
        max_scroll = max(0, total_logs - visible_logs)
        
        # Kaydırma pozisyonunu sınırla (0 ile max_scroll arasında)
        self.console_scroll_pos = max(0, min(self.console_scroll_pos, max_scroll))
        
        # Artık kaydırma değeri 0 ise en son loglar görüntülenir
        # Son loglarımızı gösterecek başlangıç indeksini hesapla
        start_idx = max(0, total_logs - visible_logs + self.console_scroll_pos)
        
        # Kaydırma rehberi - eğer en son kayıtları görmüyorsak göster
        if self.console_scroll_pos > 0:
            guide_text = f"--- Son mesajları görmek için aşağı kaydırın ({self.console_scroll_pos}) ---"
            guide_surface = self.log_font.render(guide_text, True, (180, 180, 180))
            self.console_surf.blit(guide_surface, (5, 5))
            # Rehber satırı için 1 satır düş
            visible_logs -= 1
            # Başlangıç y pozisyonu rehberden sonra
            start_y = 20
        else:
            start_y = 5
            
        # Logları çiz
        end_idx = min(start_idx + visible_logs, total_logs)
        for i, log_idx in enumerate(range(start_idx, end_idx)):
            if 0 <= log_idx < total_logs:
                text_surface = self.log_font.render(self.gameengine.logs[log_idx], True, CONSOLE_TEXT_COLOR)
                self.console_surf.blit(text_surface, (5, start_y + i * 15))
        
        # Console widget'ını güncelle
        self.console_widget.set_surface(self.console_surf)