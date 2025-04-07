from Oyun.scrabble_nesneler import *
from YapayZeka.kelime_bulucu import *
from YapayZeka.minmaks import MinimaxAI
from YapayZeka.montekarlo import MonteCarloAI
from YapayZeka.harf_analizi import LetterAnalysis
import pygame as p
import time

# TODO Improve by adding sim ?

class GameState:
    """
    Represents the current state of the Scrabble game.
    Contains the board, tile pouch, and player information.
    """
    def __init__(self, multiplier_file, tile_file):
        """
        Initialize a new game state.
        
        Args:
            multiplier_file: Path to file with board multipliers
            tile_file: Path to file with tile definitions
        """
        self.board = Board(multiplier_file)
        self.pouch = Pouch(tile_file)
        self.player_1 = Player()
        self.player_2 = Player()
        self.p1_to_play = True
        self.game_ended = False
        
        # Draw initial tiles for both players
        for _ in range(7):
            self.player_1.draw_tile(self.pouch)
            self.player_2.draw_tile(self.pouch)
            
        # Starting tile setup
        self.player_1.rack.tiles[0] = Tile('E', 1)


class GameEngine:
    """
    Core game logic for Scrabble.
    Handles moves, scoring, and AI play.
    """
    def __init__(self, gamestate, word_list_file):
        """
        Initialize the game engine.
        
        Args:
            gamestate: The GameState object
            word_list_file: Path to file with valid words
        """
        self.gamestate = gamestate
        self.word_finder = WordFinder(word_list_file, gamestate.board)
        self.exchanges = 0
        self.player_1_exchanges = 0  # Oyuncu 1'in toplam pas/değişim sayısı
        self.player_2_exchanges = 0  # Oyuncu 2'in (AI) toplam pas/değişim sayısı
        self.autoplay = False
        self.ai_possible_moves = list()  # Kod uyumluluğu için korundu, kullanılmıyor
        self.ai_possible_move_ids = list()  # Kod uyumluluğu için korundu, kullanılmıyor
        self.logs = list()
        self.ai_algorithm = "standard"  # Kullanılacak AI algoritmasını belirler: "standard", "minimax", "monte_carlo", "letter_analysis"
        self.minimax_ai = MinimaxAI(self)
        self.monte_carlo_ai = MonteCarloAI(self, simulation_time=1.0)
        self.letter_analysis = LetterAnalysis(self)
        # Her algoritmanın performansını takip etmek için istatistikler
        self.algorithm_stats = {
            "standard": {"moves": 0, "points": 0, "time": 0},
            "minimax": {"moves": 0, "points": 0, "time": 0},
            "monte_carlo": {"moves": 0, "points": 0, "time": 0},
            "letter_analysis": {"moves": 0, "points": 0, "time": 0}
        }

    def play_draft(self):
        """
        Attempt to play the currently drafted tiles on the board.
        Performs validation and scoring if the move is legal.
        """
        # Get current player based on whose turn it is
        current_player = self.gamestate.player_1 if self.gamestate.p1_to_play else self.gamestate.player_2
        is_ai_move = current_player == self.gamestate.player_2
        
        # Find the coordinates of the tiles played by the player
        played_cells = self.get_draft()
        
        # If no tiles were played, return
        if not played_cells:
            return
            
        board_obj = self.gamestate.board

        # Check if it is the first ever word and if it is check if it is played on the center
        first_play = board_obj.is_empty((7, 7), False)
        if first_play:
            for cell in played_cells:
                if cell.position == (7, 7):
                    break
            else:
                self.logs.append("İlk hamle ortada olmalı")
                return

        # Check if played tiles are in the same direction
        is_horizontal = all(cell.position[0] == played_cells[0].position[0] for cell in played_cells)
        is_vertical = all(cell.position[1] == played_cells[0].position[1] for cell in played_cells)
        if not(is_horizontal or is_vertical):
            self.logs.append("Taşlar aynı yönde olmalı")
            return
        
        # Check if played tiles are connected
        prev_pos = -1
        for cell in played_cells:
            cur_pos = cell.position[1] if is_horizontal else cell.position[0]
            if prev_pos != -1:
                for diff in range(cur_pos - prev_pos):
                    if is_horizontal and board_obj.is_empty((cell.position[0], prev_pos + diff + 1)):
                        self.logs.append("Yatay yerleştirilen taşlar bağlantılı değil.")
                        return
                    if is_vertical and board_obj.is_empty((prev_pos + diff + 1, cell.position[1])):
                        self.logs.append("Dikey yerleştirilen taşlar bağlantılı değil.")
                        return
            prev_pos = cur_pos
        
        # Check if played word is anchored to some existing word
        for cell in played_cells:
            i = cell.position[0]
            j = cell.position[1]
            if ((i > 0 and not board_obj.is_empty((i - 1, j), False)) or 
                (i < 14 and not board_obj.is_empty((i + 1, j), False)) or 
                (j > 0 and not board_obj.is_empty((i, j - 1), False)) or 
                (j < 14 and not board_obj.is_empty((i, j + 1), False))):
                break
        else:
            if not first_play:
                self.logs.append("Kelime mevcut bir taşa bağlı değil")
                return
            
        # Get all new words the player created
        main_word_cells = self.find_word_in_direction(*played_cells[0].position, is_horizontal)
        side_words_cells = list()

        for cell in played_cells:
            cur_side_word = self.find_word_in_direction(*cell.position, not is_horizontal)
            if len(cur_side_word) > 1:
                side_words_cells.append(cur_side_word)

        main_word_str = self.get_word_str_from_cells(main_word_cells)
        side_words_str = [self.get_word_str_from_cells(word_cells) for word_cells in side_words_cells]

        all_words = list()
        if not(len(main_word_str) == 1 and len(side_words_str) > 0):
            all_words.append(main_word_str)
        all_words.extend(side_words_str)

        # Check if newly formed words exist in the dictionary
        if any(not self.is_valid_word(word) for word in all_words):
            self.logs.append("Oluşturulan kelimeler geçerli değil")
            return

        # Calculate the score for each word
        main_word_score = self.calculate_score_of_word(main_word_cells)
        side_word_scores = [self.calculate_score_of_word(side_word_cells) for side_word_cells in side_words_cells]

        # Calculate the play score
        play_score = main_word_score + sum(side_word_scores)

        # Update and swap the player letters if there are enough tiles 
        current_player.rack.remove_played_tiles()
        current_player.rack.fill_empty_tiles(self.gamestate.pouch)

        # Add the score to the player and save the draft
        current_player.score += play_score

        for cell in played_cells:
            cell.tile.draft = False

        # Log who played
        if is_ai_move:
            algo_name = {
                "standard": "Standart",
                "minimax": "Minimax",
                "monte_carlo": "Monte Carlo",
                "letter_analysis": "Harf Analizi"
            }.get(self.ai_algorithm, self.ai_algorithm)
            self.logs.append(f"AI oynadı ({algo_name}, {play_score} puan)")
            self.player_2_exchanges = 0  # AI taş oynadığında değişim sayacı sıfırlanır
        else:
            self.logs.append(f"Oyuncu oynadı ({play_score} puan)")
            self.player_1_exchanges = 0  # Oyuncu taş oynadığında değişim sayacı sıfırlanır

        # Switch turns
        self.gamestate.p1_to_play = not self.gamestate.p1_to_play

        self.exchanges = 0
        self.check_game_end()

        # Make AI move if AI turn & autoplay enabled
        if not self.gamestate.p1_to_play and self.autoplay:
            p.time.wait(500)  # Add a small delay before AI moves
            self.ai_make_move()

    def ai_handle_turn(self):
        """
        Handle the AI player's turn based on current settings.
        If autoplay is enabled, makes a move automatically.
        """
        if self.autoplay:
            p.time.wait(100)  # delay for observability
            self.ai_make_move()

    def ai_make_move(self):
        """
        Have the AI player make the best move it can find.
        If no moves are possible, tries to swap tiles or pass.
        """
        try:
            # Check if it's actually AI's turn
            if self.gamestate.p1_to_play:
                self.logs.append("Şu an AI'ın sırası değil!")
                return
            
            # Get AI's rack
            current_rack = self.gamestate.player_2.rack
            
            # Find all possible moves
            all_options = self.word_finder.find_all_plays(current_rack)
            
            if len(all_options) > 0:
                # Calculate points for each possible move
                points = []
                for option in all_options:
                    try:
                        option_points, _ = self.calculate_option_point(option, True)
                        points.append(option_points)
                    except Exception as e:
                        self.logs.append(f"Puan hesaplamada hata: {str(e)}")
                        points.append(0)  # Fallback to 0 points
                
                # Make sure we have valid points
                if not points or all(p == 0 for p in points):
                    self.logs.append("Geçerli hamle puanı hesaplanamadı")
                    self.pass_turn()
                    return
                
                try:
                    # Measure time for performance comparison
                    start_time = time.time()
                    
                    # Choose the best move based on selected algorithm
                    if self.ai_algorithm == "minimax":
                        best_option_idx = self.minimax_ai.find_best_move(all_options, points)
                    elif self.ai_algorithm == "monte_carlo":
                        best_option_idx = self.monte_carlo_ai.find_best_move(all_options, points)
                    elif self.ai_algorithm == "letter_analysis":
                        analyzed_points = self.letter_analysis.analyze_moves(all_options, points)
                        best_option_idx = max(range(len(analyzed_points)), key=lambda i: analyzed_points[i])
                    else:
                        # Standard algorithm
                        best_option_idx = max(range(len(points)), key=lambda i: points[i])
                    
                    # Calculate elapsed time
                    elapsed_time = time.time() - start_time
                    
                    # Update algorithm statistics
                    self.algorithm_stats[self.ai_algorithm]["moves"] += 1
                    self.algorithm_stats[self.ai_algorithm]["time"] += elapsed_time
                    
                except Exception as e:
                    self.logs.append(f"AI hamle seçiminde hata: {str(e)}")
                    # Fallback to simple maximum
                    best_option_idx = max(range(len(points)), key=lambda i: points[i])
                
                # Play the best move
                option = all_options[best_option_idx]
                move_points = points[best_option_idx]
                
                # Update algorithm statistics with points
                self.algorithm_stats[self.ai_algorithm]["points"] += move_points
                
                # Clear any existing draft tiles before placing new ones
                self.clear_draft()
                
                # Place tiles on the board
                for cell, tile in option.items():
                    cell.tile = tile
                    tile.draft = True
                    
                # Execute the move
                self.play_draft()
            else:
                # Try to swap tiles if no moves are possible
                swapped = self.swap_draft(True)
                if not swapped:
                    # If can't swap, just pass the turn
                    self.pass_turn()
                    self.check_game_end()
        except Exception as e:
            self.logs.append(f"AI hamlesi sırasında hata: {str(e)}")
            # Emergency fallback - just pass the turn
            self.pass_turn()
            self.check_game_end()

    def clear_draft(self):
        """Remove all drafted tiles from the board."""
        for pos in self.gamestate.board.all_positions():
            cell = self.gamestate.board.board[pos[0]][pos[1]]
            if cell.tile is not None and cell.tile.draft:
                cell.tile.draft = False
                cell.tile = None

    def simulate_option_point(self, option, sim_times=1, half_depth=1):
        """
        Simulate playing a move and subsequent moves to evaluate its potential.
        
        Args:
            option: The move to simulate
            sim_times: Number of simulations to run
            half_depth: Half the number of moves to look ahead
            
        Returns:
            Average point gain from the simulations
        """
        self.clear_draft()

        # Save the current game state
        save_board_tiles = [[cell.tile for cell in self.gamestate.board.board[i]] for i in range(15)]
        save_rack_tiles_1 = self.gamestate.player_1.rack.tiles
        save_rack_tiles_2 = self.gamestate.player_2.rack.tiles
        save_score_1 = self.gamestate.player_1.score
        save_score_2 = self.gamestate.player_2.score
        save_pouch_tiles = self.gamestate.pouch.tiles
        save_p1_to_play = self.gamestate.p1_to_play
        save_game_ended = self.gamestate.game_ended
        save_exchanges = self.exchanges
        save_logs = self.logs

        # Run simulations
        total_point_gain = 0
        for _ in range(sim_times):
            # Restore state for this simulation
            self.gamestate.player_1.rack.tiles = save_rack_tiles_1.copy()
            self.gamestate.player_2.rack.tiles = save_rack_tiles_2.copy()
            self.gamestate.pouch.tiles = save_pouch_tiles.copy()
            self.gamestate.player_1.score = save_score_1
            self.gamestate.player_2.score = save_score_2
            self.gamestate.p1_to_play = save_p1_to_play
            self.gamestate.game_ended = save_game_ended
            self.exchanges = save_exchanges
            self.logs = save_logs.copy()

            # Randomize opponent's rack
            is_p1_to_play = self.gamestate.p1_to_play
            opponent = self.gamestate.player_2 if self.gamestate.p1_to_play else self.gamestate.player_1
            opponent_rack = opponent.rack
            self.gamestate.pouch.tiles += opponent_rack.tiles
            opponent_rack.tiles.clear()
            opponent_rack.fill_empty_tiles(self.gamestate.pouch)

            # Make the option move
            for cell, tile in option.items():
                cell.tile = tile
                tile.draft = True
            self.play_draft()

            # Make subsequent moves up to the specified depth
            for _ in range(half_depth * 2):
                if self.gamestate.game_ended:
                    break
                self.ai_make_move()

            # Calculate point gain from this simulation
            if is_p1_to_play:
                point_diff = (self.gamestate.player_1.score - self.gamestate.player_2.score) - (save_score_1 - save_score_2)
            else:
                point_diff = (self.gamestate.player_2.score - self.gamestate.player_1.score) - (save_score_2 - save_score_1)
            
            total_point_gain += point_diff

            # Restore the board for the next simulation
            for i in range(15):
                for j in range(15):
                    self.gamestate.board.board[i][j].tile = save_board_tiles[i][j]

        # Restore the game state completely
        self.gamestate.player_1.rack.tiles = save_rack_tiles_1
        self.gamestate.player_2.rack.tiles = save_rack_tiles_2
        self.gamestate.pouch.tiles = save_pouch_tiles
        self.gamestate.player_1.score = save_score_1
        self.gamestate.player_2.score = save_score_2
        self.gamestate.p1_to_play = save_p1_to_play
        self.gamestate.game_ended = save_game_ended
        self.exchanges = save_exchanges
        self.logs = save_logs

        # Return average point gain
        return total_point_gain / sim_times

    def calculate_option_point(self, option, return_words=False):
        """
        Calculate the points for a potential move.
        
        Args:
            option: The move to evaluate
            return_words: Whether to return the words formed
            
        Returns:
            The points scored, and optionally the words formed
        """
        # Place tiles on the board temporarily
        cells = list(option.keys())
        for cell, tile in option.items():
            cell.tile = tile
            tile.draft = True
        
        # Determine the direction of the word
        is_horizontal = True
        if len(cells) > 1:
            if cells[0].position[1] == cells[1].position[1]:
                is_horizontal = False
                
        # Find the main word and any side words formed
        main_word = self.find_word_in_direction(*cells[0].position, is_horizontal)
        side_words = list()
        for cell in cells:
            found_word = self.find_word_in_direction(*cell.position, not is_horizontal)
            if len(found_word) > 1:
                side_words.append(found_word)

        # Compile all words formed
        all_words = list()
        if not(len(main_word) == 1 and len(side_words) > 0):
            all_words.append(main_word)
        all_words.extend(side_words)
        
        # Calculate total points
        point = 0
        for word in all_words:
            point += self.calculate_score_of_word(word)
            
        # Add bonus for using all 7 tiles
        if len(cells) == 7:
            point += 50  # add bingo point

        # Return words if requested
        if return_words:
            words = list()
            for word in all_words:
                words.append(self.cells_to_word(word))
                
            # Remove tiles from the board
            for cell, tile in option.items():
                cell.tile = None
                tile.draft = False
                
            return point, words

        # Remove tiles from the board
        for cell, tile in option.items():
            cell.tile = None
            tile.draft = False

        return point

    def swap_draft(self, swap_all=False):
        """
        Swap the currently drafted tiles or all tiles.
        
        Args:
            swap_all: Whether to swap all tiles
            
        Returns:
            True if the swap was successful, False otherwise
        """
        # Get the current player
        player = self.gamestate.player_1 if self.gamestate.p1_to_play else self.gamestate.player_2
        is_ai_move = player == self.gamestate.player_2
        
        player_rack = player.rack
        is_swap_allowed = self.gamestate.pouch.tiles_amount() >= 7

        # Mark all tiles as draft if swapping all
        if is_swap_allowed and swap_all:
            for tile in player_rack.tiles:
                if tile is not None:
                    tile.draft = True

        # Count tiles to swap
        tiles_to_swap = 0
        for tile in player_rack.tiles:
            if tile is not None and tile.draft:
                tiles_to_swap += 1

        if is_swap_allowed:
            # Perform the swap
            old_tiles = list()
            for i, tile in enumerate(player_rack.tiles):
                if tile is not None and tile.draft:
                    player_rack.tiles[i] = None
                    tile.draft = False
                    old_tiles.append(tile)
            
            # Draw new tiles
            for _ in range(tiles_to_swap):
                player.draw_tile(self.gamestate.pouch)
            
            # Return old tiles to the pouch
            for tile in old_tiles: 
                self.gamestate.pouch.add_tile(tile)
            
            # End turn
            self.pass_turn()
            
            # Log the action based on who actually made the swap
            if tiles_to_swap == 0:
                # Hangi oyuncunun kaç kez değişim yaptığını göster
                exchanges_count = self.player_1_exchanges if is_ai_move == False else self.player_2_exchanges
                self.logs.append(("AI " if is_ai_move else "Oyuncu ") + 
                               f"sırayı geçti (Toplam {exchanges_count} değişim/pas)")
            else:
                # Hangi oyuncunun kaç kez değişim yaptığını göster
                exchanges_count = self.player_1_exchanges if is_ai_move == False else self.player_2_exchanges
                self.logs.append(("AI " if is_ai_move else "Oyuncu ") + 
                               f"taşlarını değiştirdi (Toplam {exchanges_count} değişim/pas)")
                
            self.check_game_end()
            return True
        else:
            # Swap failed due to insufficient tiles
            if tiles_to_swap > 0:
                self.logs.append(("AI " if is_ai_move else "Oyuncu ") + 
                               "değişim başarısız, yetersiz taş")
                return False
            else:
                # Just pass the turn if no tiles were marked for swap
                self.pass_turn()
                # Hangi oyuncunun kaç kez değişim yaptığını göster
                exchanges_count = self.player_1_exchanges if is_ai_move == False else self.player_2_exchanges
                self.logs.append(("AI " if is_ai_move else "Oyuncu ") + 
                               f"sırayı geçti (Toplam {exchanges_count} değişim/pas)")    
                self.check_game_end()
                return True

    def get_draft(self):
        """
        Get all cells with drafted tiles.
        
        Returns:
            List of cells with drafted tiles
        """
        played_cells = []
        board_obj = self.gamestate.board
        board = board_obj.board
        
        for pos in board_obj.all_positions():
            i, j = pos
            cell = board[i][j]
            if cell.tile is not None and cell.tile.draft:
                played_cells.append(cell)

        return played_cells

    def pass_turn(self):
        """Pass the current player's turn."""
        # Oyuncuya göre uygun değişim sayacını artır
        if self.gamestate.p1_to_play:
            self.player_1_exchanges += 1
            current_player_exchanges = self.player_1_exchanges
        else:
            self.player_2_exchanges += 1
            current_player_exchanges = self.player_2_exchanges
            
        # Sıra değiştir
        self.gamestate.p1_to_play = not self.gamestate.p1_to_play
        self.exchanges += 1

    def check_game_end(self):
        """Check if the game has ended and update the game state if it has."""
        # Game ends if:
        # - A player has done 4 or more exchanges/passes, or
        # - The pouch is empty and a player has no tiles
        
        # Kontrol 1: Herhangi bir oyuncu 4 veya daha fazla değişim/pas yapmış mı
        if self.player_1_exchanges >= 4:
            self.logs.append("--- OYUN BİTTİ: OYUNCU 4 KEZ DEĞİŞİM/PAS YAPTI ---")
            self.gamestate.game_ended = True
            self._show_final_scores()
            return
        
        if self.player_2_exchanges >= 4:
            self.logs.append("--- OYUN BİTTİ: AI 4 KEZ DEĞİŞİM/PAS YAPTI ---")
            self.gamestate.game_ended = True
            self._show_final_scores()
            return
            
        # Kontrol 2: Torba boş ve bir oyuncunun rafı boş
        if self.gamestate.pouch.tiles_amount() == 0:
            if self.gamestate.player_1.rack.tiles_amount() == 0:
                self.logs.append("--- OYUN BİTTİ: TORBA BOŞ VE OYUNCU 1 RAFI BOŞ ---")
                self.gamestate.game_ended = True
                self._show_final_scores()
                return
            elif self.gamestate.player_2.rack.tiles_amount() == 0:
                self.logs.append("--- OYUN BİTTİ: TORBA BOŞ VE OYUNCU 2 (AI) RAFI BOŞ ---")
                self.gamestate.game_ended = True
                self._show_final_scores()
                return
                
    def _show_final_scores(self):
        """Oyun bittiğinde final skorları gösterir ve kazananı belirler."""
        player1_score = self.gamestate.player_1.score
        player2_score = self.gamestate.player_2.score
        
        self.logs.append("==== FİNAL SKORLARI ====")
        self.logs.append(f"OYUNCU 1: {player1_score}")
        self.logs.append(f"OYUNCU 2 (AI): {player2_score}")
        
        if player1_score > player2_score:
            self.logs.append("KAZANAN: OYUNCU 1!")
        elif player2_score > player1_score:
            self.logs.append("KAZANAN: OYUNCU 2 (AI)!")
        else:
            self.logs.append("SONUÇ: BERABERE!")

    def calculate_score_of_word(self, word_cells):
        """
        Calculate the score for a word.
        
        Args:
            word_cells: List of cells forming the word
            
        Returns:
            The score for the word
        """
        word_score = 0
        word_multiplier = 1
        
        for cell in word_cells:
            point = cell.tile.point
            
            # Apply multipliers only for newly placed tiles
            if cell.tile.draft:
                letter_multiplier = cell.multiplier
                if letter_multiplier == "DL":
                    point *= 2
                elif letter_multiplier == "TL":
                    point *= 3
                elif letter_multiplier == "DW":
                    word_multiplier *= 2
                elif letter_multiplier == "TW":
                    word_multiplier *= 3

            word_score += point

        # Apply word multiplier
        word_score *= word_multiplier

        return word_score

    def cells_to_word(self, cells):
        """
        Convert a list of cells to a word string.
        
        Args:
            cells: List of cells
            
        Returns:
            String representation of the word
        """
        word = ""
        for cell in cells:
            word += cell.tile.letter
        return word

    def find_word_in_direction(self, i, j, is_horizontal):
        """
        Find a word starting from a position in a given direction.
        
        Args:
            i: Row index
            j: Column index
            is_horizontal: Whether to search horizontally
            
        Returns:
            List of cells forming the word
        """
        cur_i = i
        cur_j = j
        cells = list()
        board_obj = self.gamestate.board
        board = board_obj.board
        
        if is_horizontal:
            # Move to the beginning of the word
            while board_obj.has_left((cur_i, cur_j)):
                cur_j -= 1
                
            # Collect all cells to the end of the word
            while board_obj.has_right((cur_i, cur_j)):
                cells.append(board[cur_i][cur_j])
                cur_j += 1
                
            # Add the last cell
            cells.append(board[cur_i][cur_j])
        else:
            # Move to the beginning of the word
            while board_obj.has_up((cur_i, cur_j)):
                cur_i -= 1
                
            # Collect all cells to the end of the word
            while board_obj.has_down((cur_i, cur_j)):
                cells.append(board[cur_i][cur_j])
                cur_i += 1
                
            # Add the last cell
            cells.append(board[cur_i][cur_j])

        return cells

    def get_word_str_from_cells(self, cells):
        """
        Get a string representation of a word from cells.
        
        Args:
            cells: List of cells
            
        Returns:
            String representation of the word
        """
        word = ""
        for cell in cells:
            word += cell.tile.letter
        return word

    def is_valid_word(self, word):
        """
        Check if a word is valid.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is valid, False otherwise
        """
        return self.word_finder.trie.is_word(word)

    def get_algorithm_performance(self):
        """
        AI algoritmalarının performans istatistiklerini döndür
        
        Returns:
            Dict: Her algoritma için performans istatistikleri
        """
        # Her algoritma için ortalama değerleri hesapla
        result = {}
        for algo, stats in self.algorithm_stats.items():
            moves = stats["moves"]
            if moves > 0:
                avg_points = stats["points"] / moves
                avg_time = stats["time"] / moves
                result[algo] = {
                    "moves": moves,
                    "avg_points": avg_points,
                    "avg_time": avg_time,
                    "total_points": stats["points"]
                }
            else:
                result[algo] = {
                    "moves": 0,
                    "avg_points": 0,
                    "avg_time": 0,
                    "total_points": 0
                }
        return result

    def end_game_manually(self):
        """
        Oyuncunun oyunu manuel olarak sonlandırmasını sağlar.
        Bu fonksiyon, ekrandaki 'OYUNU BİTİR' butonuna basıldığında çağrılır.
        """
        self.logs.append("--- OYUN MANUEL OLARAK SONLANDIRILDI ---")
        self.gamestate.game_ended = True
        self._show_final_scores()
        return

    def play_option(self, option_idx):
        """
        Eski hamleler listesinden oynatma metodu.
        Artık kullanılmıyor, fakat kod uyumluluğu için korundu.
        """
        pass