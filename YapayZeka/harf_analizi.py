class LetterAnalysis:
    """
    Kalan harflerin dağılımını analiz ederek hamle stratejisini belirleyen sınıf.
    Nadir harfleri stratejik olarak kullanmayı sağlar.
    """
    def __init__(self, game_engine):
        """
        Harf analizi sınıfını başlat
        
        Args:
            game_engine: Oyun motoru referansı
        """
        self.game_engine = game_engine
        self.letter_values = {}
        self._init_letter_values()
        
    def _init_letter_values(self):
        """Harflerin değerlerini başlat"""
        for tile in self.game_engine.gamestate.pouch.tiles:
            if tile.letter in self.letter_values:
                self.letter_values[tile.letter]['count'] += 1
            else:
                self.letter_values[tile.letter] = {
                    'count': 1,
                    'points': tile.point
                }
    
    def analyze_moves(self, possible_moves, points_list):
        """
        Olası hamleleri harf dağılımı açısından analiz eder
        
        Args:
            possible_moves: Olası hamlelerin listesi
            points_list: Her hamlenin getirdiği puanlar
            
        Returns:
            Yeni bir puan listesi (stratejik değeri eklenmiş)
        """
        new_points = points_list.copy()
        
        # Kalan harflerin durumunu analiz et
        remaining_letters = self._analyze_remaining_letters()
        
        for i, move in enumerate(possible_moves):
            # Hamlede kullanılan harfleri bul
            used_letters = []
            for cell, tile in move.items():
                if cell.tile is None or cell.tile.draft:  # Sadece yeni eklenen harfleri say
                    used_letters.append(tile.letter)
            
            # Stratejik değer hesapla
            strategic_value = self._calculate_strategic_value(used_letters, remaining_letters)
            
            # Orijinal puana stratejik değeri ekle
            new_points[i] += strategic_value
            
        return new_points
    
    def _analyze_remaining_letters(self):
        """
        Oyunda kalan harflerin dağılımını analiz eder
        
        Returns:
            Harflerin kalan sayıları ve stratejik değerleri
        """
        # Torbada ve tahtada kalan harfleri say
        remaining = {}
        
        # Başlangıçtaki değerleri kopyala
        for letter, data in self.letter_values.items():
            remaining[letter] = {
                'count': data['count'],
                'points': data['points'],
                'strategic_value': 0
            }
        
        # Tahtadaki harfleri çıkar
        for pos in self.game_engine.gamestate.board.all_positions():
            cell = self.game_engine.gamestate.board.get_pos(pos)
            if cell.tile is not None and not cell.tile.draft:
                letter = cell.tile.letter
                if letter in remaining:
                    remaining[letter]['count'] -= 1
        
        # Oyuncuların elindeki harfleri çıkar
        for player in [self.game_engine.gamestate.player_1, self.game_engine.gamestate.player_2]:
            for tile in player.rack.tiles:
                if tile is not None:
                    letter = tile.letter
                    if letter in remaining:
                        remaining[letter]['count'] -= 1
        
        # Stratejik değerleri hesapla
        total_remaining = sum(data['count'] for data in remaining.values())
        if total_remaining > 0:
            for letter, data in remaining.items():
                # Nadir harfler daha değerli
                rarity = 1.0 - (data['count'] / total_remaining)
                # Puanı yüksek harfler daha değerli
                point_value = data['points'] / 4.0  # Normalize et
                
                # Stratejik değer: nadir ve değerli harfler daha önemli
                data['strategic_value'] = rarity * 3.0 + point_value * 2.0
                
        return remaining
    
    def _calculate_strategic_value(self, used_letters, remaining_letters):
        """
        Kullanılan harflerin stratejik değerini hesaplar
        
        Args:
            used_letters: Hamlede kullanılan harfler
            remaining_letters: Kalan harflerin analizi
            
        Returns:
            Stratejik değer
        """
        if not used_letters:
            return 0
            
        strategic_value = 0
        for letter in used_letters:
            if letter in remaining_letters:
                # Sık kullanılan harfleri tercih et, nadir harfleri sakla
                letter_value = remaining_letters[letter]['strategic_value']
                if remaining_letters[letter]['count'] <= 2:
                    # Nadir harf kullanılırsa puan kır
                    strategic_value -= letter_value * 1.5
                else:
                    # Sık harf kullanılırsa bonus ver
                    strategic_value += 0.5
                    
        return strategic_value 