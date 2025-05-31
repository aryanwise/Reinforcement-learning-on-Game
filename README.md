Zombie Shooter: Survival

- Aryan Mishra; Project for Uni- GISMA, Course- AI_Studio [GH-1027140]

  A fast-paced 2D zombie shooter built with Pygame, inspired by arcade classics. Survive three escalating phases of zombie hordes, move freely with WASD, aim with arrow keys, and double-tap to shoot. Rack up kills, avoid hits, and see how long you can last in this post-apocalyptic grind!
  Features

Free Movement: Roam the 800x600 arena with WASD controls.
Three Phases: Face increasing zombie waves:
Phase 1: Slow zombies, sparse spawns (every 1.5s), 30 seconds.
Phase 2: Faster zombies, more spawns (every 1s), 30 seconds.
Phase 3: Rapid zombies, frequent spawns (every 0.5s), until you fall.

Aiming System: Cyan arrow shows aim direction, controlled by arrow keys.
Double-Tap Shooting: Double-tap an arrow key to fire bullets in the aim direction.
Health & Score: 3 health points, score points per zombie kill.
HUD: Displays health, score, and current phase.
Game Over: Shows final score and phase reached, exits after 3 seconds.

Requirements

Python 3.8+
Pygame 2.6.0

Installation

Clone or download this repository:git clone <repo-url>
cd zombie-shooter

Create a virtual environment (optional but recommended):python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies:pip install -r requirements.txt

Run the game:python zombie_shooter_improved.py

Controls

Move: WASD (W: up, A: left, S: down, D: right).
Aim: Arrow keys (up, down, left, right) to set aim direction (shown by cyan arrow).
Shoot: Double-tap an arrow key within 0.3 seconds to fire a bullet.
Quit: Close the window or press the exit button.

Gameplay

Objective: Survive as long as possible across three zombie phases, scoring kills.
Phases:
Phase 1: Easy, slow zombies, lasts 30 seconds.
Phase 2: Medium, faster and more zombies, lasts 30 seconds.
Phase 3: Hard, rapid spawns and fast zombies, continues until game over.

Health: Start with 3 health. Zombies touching you reduce health by 1. Game over at 0 health.
Scoring: +1 point per zombie killed.
Zombies: Spawn at random edges (top, bottom, left, right) and chase you.
Bullets: Fired in aim direction, disappear off-screen.

Development

Language: Python 3 with Pygame.
Structure:
zombie_shooter_improved.py: Main game script.
requirements.txt: Dependencies.

Assets: Placeholder surfaces (green player, red zombies, white bullets, cyan arrow). Replace with sprites for better visuals.

Future Improvements

Sprites: Add pixel art for player, zombies, and bullets (e.g., from itch.io).
Sounds: Include shooting and kill sounds (e.g., from Freesound.org).
Power-Ups: Add health or speed boosts as collectibles.
Background: Use a tiled post-apocalyptic image.
Cooldown: Add a shooting cooldown to balance double-tap.
Restart: Implement ‘R’ key to reset game.
Animations: Add hit flashes or death explosions.

Contributing
Wanna make this game even sicker? Fork the repo, tweak the code, and submit a pull request. Ideas:

New zombie types (e.g., fast or tanky).
Weapon upgrades (e.g., shotgun spread).
Leaderboard for high scores.

License
MIT License. Feel free to use, modify, and share.
Credits
Built by a coder with a passion for arcade shooters, inspired by zombie classics. Respect to the Pygame community!

Survive the horde, my G! 🧟‍♂️
