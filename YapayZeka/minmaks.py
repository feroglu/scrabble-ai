class MinimaxAI:
    """
    Minimax algoritması kullanan bir AI sınıfı.
    Sınırlı bir derinlikte, mümkün olan hamleleri değerlendirerek en iyi hamleyi seçer.
    """
    def __init__(self, game_engine, max_depth=2):
        """
        Minimax AI sınıfını başlat
        
        Args:
            game_engine: Oyun motoru referansı
            max_depth: Maksimum arama derinliği
        """
        self.game_engine = game_engine
        self.max_depth = max_depth
        
    def find_best_move(self, possible_moves, possible_points):
        """
        Mevcut durumda en iyi hamleyi bul
        
        Args:
            possible_moves: Olası hamleler listesi
            possible_points: Her hamlenin puanı
            
        Returns:
            En iyi hamlenin indeksi
        """
        if not possible_moves:
            return -1
            
        # Save initial game state
        init_board = self.copy_board()
        init_p1_rack = self.game_engine.gamestate.player_1.rack.tiles.copy()
        init_p2_rack = self.game_engine.gamestate.player_2.rack.tiles.copy()
        init_p1_score = self.game_engine.gamestate.player_1.score
        init_p2_score = self.game_engine.gamestate.player_2.score
        init_p1_to_play = self.game_engine.gamestate.p1_to_play
        init_pouch_tiles = self.game_engine.gamestate.pouch.tiles.copy()
        
        best_score = float('-inf')
        best_move_idx = 0
        
        # Evaluate each possible move
        for i, (move, points) in enumerate(zip(possible_moves, possible_points)):
            # Try placing the tiles on the board temporarily
            for cell, tile in move.items():
                cell.tile = tile
                
            # Evaluate this move with minimax
            current_score = points
            future_score = self.minimax(1, False, current_score)
            total_score = current_score + future_score
            
            # Restore initial state
            self.restore_game_state(init_board, init_p1_rack, init_p2_rack, 
                                    init_p1_score, init_p2_score, init_p1_to_play,
                                    init_pouch_tiles)
            
            # Update best move if this one is better
            if total_score > best_score:
                best_score = total_score
                best_move_idx = i
                
        return best_move_idx
        
    def minimax(self, depth, is_maximizing, current_score):
        """
        Minimax algoritması - gelecekteki olası hamleleri değerlendirir
        
        Args:
            depth: Mevcut derinlik
            is_maximizing: Maksimize eden oyuncunun sırası mı
            current_score: Şu ana kadar olan puan
            
        Returns:
            En iyi hamlenin değeri
        """
        # Base case: max depth reached or game ended
        if depth == self.max_depth or self.game_engine.gamestate.game_ended:
            return 0
            
        # Save current game state
        curr_board = self.copy_board()
        curr_p1_rack = self.game_engine.gamestate.player_1.rack.tiles.copy()
        curr_p2_rack = self.game_engine.gamestate.player_2.rack.tiles.copy()
        curr_p1_score = self.game_engine.gamestate.player_1.score
        curr_p2_score = self.game_engine.gamestate.player_2.score
        curr_p1_to_play = self.game_engine.gamestate.p1_to_play
        curr_pouch_tiles = self.game_engine.gamestate.pouch.tiles.copy()
        
        if is_maximizing:
            # AI's turn (trying to maximize score)
            best_value = float('-inf')
            
            # Get AI rack
            ai_rack = self.game_engine.gamestate.player_2.rack
            
            # Find possible moves for AI
            all_options = self.game_engine.word_finder.find_all_plays(ai_rack)
            
            # If no options, return current score (no change)
            if not all_options:
                return 0
                
            # Consider only top 2 options to limit branching
            top_options = sorted(all_options, 
                                key=lambda option: self.game_engine.calculate_option_point(option),
                                reverse=True)[:2]
                                
            for option in top_options:
                # Calculate immediate points
                option_points = self.game_engine.calculate_option_point(option)
                
                # Try placing the tiles on the board temporarily
                for cell, tile in option.items():
                    cell.tile = tile
                    
                # Recursive evaluation
                future_value = self.minimax(depth + 1, False, current_score + option_points)
                best_value = max(best_value, option_points + future_value)
                
                # Restore game state
                self.restore_game_state(curr_board, curr_p1_rack, curr_p2_rack, 
                                      curr_p1_score, curr_p2_score, curr_p1_to_play,
                                      curr_pouch_tiles)
                
            return best_value
        else:
            # Opponent's turn (AI is trying to minimize)
            best_value = float('inf')
            
            # Get player rack
            player_rack = self.game_engine.gamestate.player_1.rack
            
            # Find possible moves for player
            all_options = self.game_engine.word_finder.find_all_plays(player_rack)
            
            # If no options, return current score (no change)
            if not all_options:
                return 0
                
            # Consider only top 2 options to limit branching
            top_options = sorted(all_options, 
                                key=lambda option: self.game_engine.calculate_option_point(option),
                                reverse=True)[:2]
                                
            for option in top_options:
                # Calculate immediate points
                option_points = self.game_engine.calculate_option_point(option)
                
                # Try placing the tiles on the board temporarily
                for cell, tile in option.items():
                    cell.tile = tile
                    
                # Recursive evaluation
                future_value = self.minimax(depth + 1, True, current_score - option_points)
                best_value = min(best_value, -option_points + future_value)
                
                # Restore game state
                self.restore_game_state(curr_board, curr_p1_rack, curr_p2_rack, 
                                      curr_p1_score, curr_p2_score, curr_p1_to_play,
                                      curr_pouch_tiles)
                
            return best_value
    
    def copy_board(self):
        """Tahtanın mevcut durumunun kopyasını al"""
        board_copy = []
        for row in self.game_engine.gamestate.board.board:
            row_copy = []
            for cell in row:
                row_copy.append(cell.tile)
            board_copy.append(row_copy)
        return board_copy
    
    def restore_game_state(self, board, p1_rack, p2_rack, p1_score, p2_score, p1_to_play, pouch_tiles):
        """Oyunun durumunu kaydedilen state'e geri yükle"""
        # Restore board
        for i, row in enumerate(board):
            for j, tile in enumerate(row):
                self.game_engine.gamestate.board.board[i][j].tile = tile
                
        # Restore racks
        self.game_engine.gamestate.player_1.rack.tiles = p1_rack.copy()
        self.game_engine.gamestate.player_2.rack.tiles = p2_rack.copy()
        
        # Restore scores
        self.game_engine.gamestate.player_1.score = p1_score
        self.game_engine.gamestate.player_2.score = p2_score
        
        # Restore turn
        self.game_engine.gamestate.p1_to_play = p1_to_play
        
        # Restore pouch
        self.game_engine.gamestate.pouch.tiles = pouch_tiles.copy()
    
    def evaluate_move(self, move_points):
        """
        Bir hamlenin değerini hesapla (basit skor değerlendirmesi)
        
        Args:
            move_points: Hamlenin puanı
            
        Returns:
            Değerlendirme skoru
        """
        # We could add heuristics here in the future
        return move_points 