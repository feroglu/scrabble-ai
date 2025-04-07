from Arayuz import scrabble_goruntu
from Oyun import scrabble_motor, scrabble_nesneler
import pygame as p


def main():
    """
    Main function that initializes and runs the Scrabble game.
    """
    # Initialize the game state and engine
    gamestate = scrabble_motor.GameState('Veri/carpanlar.txt', 'Veri/lang/tr/tiles.txt')
    gameengine = scrabble_motor.GameEngine(gamestate, 'Veri/lang/tr/turkce_kelime_listesi.txt')

    # Create the renderer
    renderer = scrabble_goruntu.Renderer(gamestate, gameengine)
    
    # Konsol kaydırma için değişken ekle (aşağıda kullanılacak)
    renderer.console_scroll_pos = 0

    # Initialize pygame
    p.init()

    # Create the game window
    screen = p.display.set_mode((scrabble_goruntu.WINDOW_WIDTH, scrabble_goruntu.WINDOW_HEIGHT))
    p.display.set_caption("Scrabble AI Game")

    # Initialize UI components
    renderer.init_pymenus()
    renderer.init_location_rects()

    # Set up game clock for framerate control
    clock = p.time.Clock()

    # Initialize drag-and-drop variables
    dragging = False
    drag_mode_board = False  # True if dragging from board, False if from rack
    drag_old_pos = (-1, -1)  # Original position of the dragged tile
    dragging_tile = None     # The tile being dragged
    drag_surf = p.Surface((scrabble_goruntu.SQ_SIZE, scrabble_goruntu.SQ_SIZE))

    # Main game loop
    running = True
    while running:
        # Get all pygame events
        events = p.event.get()
        
        # Create a surface for the current frame
        game_surf = p.Surface((scrabble_goruntu.WINDOW_WIDTH, scrabble_goruntu.WINDOW_HEIGHT))           

        # Update UI menus with events
        renderer.ai_opt_btn_sec.update(events)
        renderer.ai_possible_moves_sec.update(events)
        renderer.player_btn_sec.update(events)
        renderer.ai_algorithm_sec.update(events)
        renderer.end_game_sec.update(events)  # Oyunu bitir düğmesini güncelle
        
        # Render the game state
        renderer.render_game(game_surf)

        # Handle events
        for event in events:
            if event.type == p.QUIT:
                running = False
                
            # Çıkış düğmesinin kontrolü
            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:  # ESC tuşu basılırsa
                    running = False
                
            elif event.type == p.MOUSEBUTTONDOWN:
                # Handle button clicks
                if event.button == 1:  # Left click
                    # Check if clicked on exit button (bu kısım fonksiyonun kendisine yönlendirecek)
                    if renderer.end_game_sec.get_widget("end_game").get_rect().collidepoint(event.pos):
                        print("Oyunu Bitir düğmesine tıklandı")
                        # Doğrudan kapatmak yerine, buton işlevini çağır
                        # Bu şekilde sadece renderer'ın handle_end_game_button metodu çağrılacak
                
                # Eğer oyun bitmişse diğer tıklamaları işleme
                if gamestate.game_ended:
                    continue  # Oyun bittiyse diğer tıklamaları işleme
                
                if gamestate.p1_to_play:  # Only handle player 1 input
                    if not renderer.swap_mode:  # Normal play mode
                        if event.button == 1:  # Left click
                            # Check if click is on board or rack
                            board_is_col, board_tile = renderer.board_col_detect(*event.pos)
                            rack_is_col, rack_tile = renderer.rack_col_detect(*event.pos)
                            
                            if board_is_col or rack_is_col:
                                # Handle board click - pick up a drafted tile
                                if board_is_col:
                                    cell = gamestate.board.board[board_tile[0]][board_tile[1]]
                                    tile_to_drag = cell.tile
                                    if tile_to_drag is not None and tile_to_drag.draft:
                                        cell.tile = None
                                        dragging = True
                                        drag_mode_board = True
                                        drag_old_pos = board_tile
                                        dragging_tile = tile_to_drag

                                # Handle rack click - pick up a tile from rack
                                if rack_is_col:
                                    tile_to_drag = gamestate.player_1.rack.tiles[rack_tile]
                                    if tile_to_drag is not None and not tile_to_drag.draft:
                                        dragging = True
                                        drag_mode_board = False
                                        drag_old_pos = rack_tile
                                        dragging_tile = tile_to_drag
                                        dragging_tile.draft = True
                        if event.button == 3:  # Right click - remove tile from board
                            board_is_col, board_tile = renderer.board_col_detect(*event.pos)
                            if board_is_col:
                                cell = gamestate.board.board[board_tile[0]][board_tile[1]]
                                tile = cell.tile
                                if tile is not None and tile.draft:
                                    cell.tile = None
                                    tile.draft = False
                    else:  # Swap mode
                        if event.button == 1:  # Left click - toggle draft status for swap
                            rack_is_col, rack_tile = renderer.rack_col_detect(*event.pos)
                            if rack_is_col:
                                tile_to_drag = gamestate.player_1.rack.tiles[rack_tile]
                                if tile_to_drag is not None:
                                    tile_to_drag.draft = not tile_to_drag.draft
                                    
                # Kontrol konsol kaydırma için fare tekerleği olayı
                # Fare konsolun üzerinde mi kontrol et - koordinatları düzelt
                if 800 < event.pos[0] < 1175 and 380 < event.pos[1] < 630:
                    if event.button == 4:  # Yukarı kaydırma (tekerleği yukarı) - Ekranı yukarı kaydırır, yani scroll değerini artırır
                        # Maksimum kaydırma sınırı
                        visible_logs_max = 18
                        visible_logs = min(visible_logs_max, len(gameengine.logs))
                        max_scroll = max(0, len(gameengine.logs) - visible_logs)
                        # Kaydırma değerini artır (yukarı doğru)
                        renderer.console_scroll_pos = min(max_scroll, renderer.console_scroll_pos + 3)  # Daha hızlı kaydırma
                    elif event.button == 5:  # Aşağı kaydırma (tekerleği aşağı) - Ekranı aşağı kaydırır, yani scroll değerini azaltır
                        # Kaydırma değerini azalt (aşağı doğru, 0=en alt)
                        renderer.console_scroll_pos = max(0, renderer.console_scroll_pos - 3)  # Daha hızlı kaydırma
                            
            elif event.type == p.MOUSEBUTTONUP:
                if gamestate.p1_to_play:
                    if not renderer.swap_mode:
                        if event.button == 1 and dragging:  # Left mouse button release while dragging
                            if not drag_mode_board:  # Dragging from rack
                                board_is_col, board_tile = renderer.board_col_detect(*event.pos)
                                if not board_is_col:  # Not dropped on board
                                    dragging_tile.draft = False
                                    dragging = False
                                else:  # Dropped on board
                                    cell = gamestate.board.board[board_tile[0]][board_tile[1]]
                                    cell.tile = dragging_tile
                                    dragging = False
                            else:  # Dragging from board
                                board_is_col, board_tile = renderer.board_col_detect(*event.pos)
                                if board_is_col:  # Dropped on board
                                    cell = gamestate.board.board[board_tile[0]][board_tile[1]]
                                    if cell.tile is None:  # Cell is empty
                                        cell.tile = dragging_tile
                                        dragging = False
                                    else:  # Cell already has a tile, return to original position
                                        old_cell = gamestate.board.board[drag_old_pos[0]][drag_old_pos[1]]
                                        old_cell.tile = dragging_tile
                                        dragging = False
                                else:  # Not dropped on board, return to original position
                                    old_cell = gamestate.board.board[drag_old_pos[0]][drag_old_pos[1]]
                                    old_cell.tile = dragging_tile
                                    dragging = False

        # Render the dragged tile at the mouse position
        if dragging:
            renderer.render_tile(dragging_tile, drag_surf)
            game_surf.blit(drag_surf, (event.pos[0] - scrabble_goruntu.SQ_SIZE // 2, 
                                      event.pos[1] - scrabble_goruntu.SQ_SIZE // 2))

        # Draw the game surface to the screen
        screen.blit(game_surf, (0, 0))

        # Update the display
        p.display.flip()

        # Control the game framerate
        clock.tick(scrabble_goruntu.MAX_FPS)

    # Clean up pygame resources when done
    p.quit()


if __name__ == "__main__":
    main()