# Scrabble AI

This project implements a Scrabble board game with multiple artificial intelligence algorithms for the YAP 441 Artificial Intelligence course.

![Game Image](https://i.imgur.com/tJLENQl.png)

## How to Run

Run `python scrabble.py` in the base directory. 

Requirements:
- Python 3.6+
- pygame
- pygame-menu

## Controls

- **Tile Placement**: Drag and drop tiles from your rack to the board
- **Tile Removal**: Right-click a placed tile to return it to the rack
- **Exchange Tiles**: Click "DEĞİŞTİR" to exchange selected tiles
- **Play Move**: Click "OYNA" to confirm your move
- **AI Play**: Click "AI OYNA" for a single AI move
- **Autoplay**: Toggle "OTOMATİK" for continuous AI play
- **End Game**: Click "OYUNU BİTİR" to end the game manually

## Project Structure

The project follows a modular architecture with four main components:

1. **Arayuz (Interface)**: Handles the graphical representation and user interaction
2. **Oyun (Game)**: Implements game logic and mechanics
3. **Veri (Data)**: Contains the dictionary, tile values, and multiplier information
4. **YapayZeka (AI)**: Houses the artificial intelligence algorithms

## AI Algorithms

The game includes four distinct AI algorithms:

1. **Standard** - Maximizes immediate score by finding the highest-scoring move
2. **Minimax** - Uses strategic depth by looking ahead at possible opponent responses
3. **Monte Carlo** - Uses probabilistic simulations to estimate move quality
4. **Letter Analysis** - Analyzes the distribution of remaining letters for strategic tile management

You can select different AI algorithms using the dropdown menu in the game interface.

## Features

- Turkish language support with ~120,000 words dictionary
- Trie data structure for efficient word validation
- Drag-and-drop interface for intuitive gameplay
- Performance statistics in the console, tracking:
  - Points scored per move
  - Decision time for AI algorithms
  - Total score accumulated by each algorithm
- Algorithm comparison during gameplay

## Project Files

- `scrabble.py`: Main game file that initializes the game
- `Arayuz/`: Contains UI-related code including `scrabble_goruntu.py`
- `Oyun/`: Contains game logic in `scrabble_motor.py` and `scrabble_nesneler.py`
- `Veri/`: Contains data files like the word list and board multipliers
- `YapayZeka/`: Contains AI algorithms (`kelime_bulucu.py`, `minmaks.py`, `montekarlo.py`, `harf_analizi.py`, `trie.py`)