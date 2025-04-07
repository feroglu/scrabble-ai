import random
import math
import time

class MonteCarloAI:
    """
    Monte Carlo Tree Search algoritması kullanan bir AI sınıfı.
    Rastgele simülasyonlar yaparak en iyi hamleyi seçer.
    """
    def __init__(self, game_engine, simulation_time=1.0):
        """
        Monte Carlo AI sınıfını başlat
        
        Args:
            game_engine: Oyun motoru referansı
            simulation_time: Simülasyon için ayrılan maksimum süre (saniye)
        """
        self.game_engine = game_engine
        self.simulation_time = simulation_time
        self.exploration_weight = 1.0
        
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
            
        # Simülasyon sayacı
        num_simulations = 0
        
        # Her hamle için skor ve simülasyon sayısı tutacak
        move_stats = [(0, 0) for _ in range(len(possible_moves))]  # (total_score, num_simulations)
        
        # Simülasyon için ayrılan süreyi kontrol et
        start_time = time.time()
        end_time = start_time + self.simulation_time
        
        # İlk olarak her hamleyi en az bir kez simüle et
        for i in range(len(possible_moves)):
            score = self.run_simulation(possible_moves[i], possible_points[i])
            move_stats[i] = (score, 1)
            num_simulations += 1
            
            # Süre kontrolü
            if time.time() >= end_time:
                break
                
        # Kalan süre için UCB1 algoritmasıyla hamle seç ve simüle et
        while time.time() < end_time:
            # UCB1 formülü kullanarak en iyi hamleyi seç
            selected_idx = self.select_move(move_stats, num_simulations)
            
            # Seçilen hamleyi simüle et
            score = self.run_simulation(possible_moves[selected_idx], possible_points[selected_idx])
            
            # Sonuçları güncelle
            total_score, sim_count = move_stats[selected_idx]
            move_stats[selected_idx] = (total_score + score, sim_count + 1)
            num_simulations += 1
            
        # En yüksek ortalama skora sahip hamleyi seç
        best_move_idx = max(range(len(move_stats)), 
                           key=lambda i: move_stats[i][0] / max(1, move_stats[i][1]))
                           
        return best_move_idx
        
    def select_move(self, move_stats, total_simulations):
        """
        UCB1 algoritması kullanarak bir sonraki simüle edilecek hamleyi seç
        
        Args:
            move_stats: Hamlelerin istatistikleri (total_score, num_simulations)
            total_simulations: Toplam simülasyon sayısı
            
        Returns:
            Seçilen hamlenin indeksi
        """
        ucb_values = []
        for total_score, sim_count in move_stats:
            if sim_count == 0:
                ucb_values.append(float('inf'))  # Henüz simüle edilmemiş hamleleri teşvik et
            else:
                # UCB1 formülü: average_score + exploration_weight * sqrt(ln(total_simulations) / sim_count)
                average_score = total_score / sim_count
                exploration = self.exploration_weight * math.sqrt(math.log(total_simulations) / sim_count)
                ucb_values.append(average_score + exploration)
                
        return ucb_values.index(max(ucb_values))
        
    def run_simulation(self, move, immediate_points):
        """
        Bir hamleyi simüle et ve sonuç skorunu döndür
        
        Args:
            move: Simüle edilecek hamle
            immediate_points: Hamlenin anında kazandırdığı puan
            
        Returns:
            Simülasyon sonucundaki toplam skor
        """
        # Save current game state
        board = self.copy_board()
        p1_rack = self.game_engine.gamestate.player_1.rack.tiles.copy()
        p2_rack = self.game_engine.gamestate.player_2.rack.tiles.copy()
        p1_score = self.game_engine.gamestate.player_1.score
        p2_score = self.game_engine.gamestate.player_2.score
        p1_to_play = self.game_engine.gamestate.p1_to_play
        pouch_tiles = self.game_engine.gamestate.pouch.tiles.copy()
        
        # Simulate the move by temporarily placing tiles
        for cell, tile in move.items():
            cell.tile = tile
            
        # Random simulation - just add immediate points
        total_score = immediate_points
        
        # Add a small random factor to introduce exploration
        random_factor = random.uniform(0.8, 1.2)
        total_score *= random_factor
        
        # For future improvement: simulate a few random moves ahead
        # and evaluate final position
        
        # Restore game state
        self.restore_game_state(board, p1_rack, p2_rack, p1_score, p2_score, p1_to_play, pouch_tiles)
        
        return total_score
        
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