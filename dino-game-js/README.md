# Dino Runner — Chrome Dinosaur Game Clone

*A browser clone of the offline Chrome dinosaur endless‑runner, built from scratch in vanilla JavaScript with the HTML5 Canvas.*

![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Canvas](https://img.shields.io/badge/HTML5-Canvas-orange)
![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

## Overview

Press **Space** to jump, dodge the cacti and pterodactyls, and survive as the game speeds up. This is a from‑scratch recreation of the classic Chrome offline game — **no frameworks, no libraries**, just ES6 classes and a `requestAnimationFrame` game loop with rectangular collision detection.

## How to Play

- **Space** — jump.
- Avoid ground obstacles (**cacti**) and flying obstacles (**pterodactyls**).
- The game gradually accelerates; your score increases the longer you last.
- After a game over, press **Space** to play again.

## Project Structure

```
index.html       # Entry page (mounts the canvas)
main.js          # Bootstraps the canvas and starts the Game
game.js          # Game engine: loop, collisions, score, difficulty, pause/end
dino.js          # Player: gravity, jump physics, sprite rendering
cactus.js        # Ground obstacle + spawner
pterodactyl.js   # Flying obstacle + spawner
collision.js     # Rectangle collision detection + vector helpers
canvas.js        # Canvas context & drawing helpers
lib/dom.js       # Tiny DOM helper
lib/list.js      # Tiny list helper
pngegg.png       # Dino sprite
main.css         # Styling
```

## How to Run

Just open `index.html` in any modern web browser — no build step or server needed.

## Notes

- Pure vanilla JS: a compact demonstration of a game loop, sprite physics, and collision detection without any engine.
- Built for an *Information Architecture Design & Practice* course assignment.
