# Magic Cigarette
This is a small, retro-inspired "brick breaker" game I developed for an anti-smoking workshop for elementary school students in Cambodia, where smoking is a leading cause of death. It was inspired by [this image](https://digitaladvocacycenter.com/en/pong-game-in-the-shape-of-lungs/) of a Pong-like game with blocks arranged in the shape of lungs. Built with Python and Pyxel, this game was designed as an interactive and engaging educational tool for students to better understand the adverse affects of smoking on the lungs.

<p align="center">
  <img src="https://github.com/panpov/magic-cigarette/blob/main/title.png" alt="title screen">
  <img src="https://github.com/panpov/magic-cigarette/blob/main/preview.gif" alt="game preview">
</p>

## Gameplay
- You are in possession of a magic cigarette that can endlessly regenerate itself. You never have to buy another one again!
- Smoke faster! How quickly can you smoke? Let's find out! There's a timer in the top left of the screen that tells you how long you have been smoking the magic cigarette. 
- Smoke correctly! You have to drag on the cigarette for some time to unleash its full potential, and do so on your lungs—the enemy.
- Watch out! The smoke is quite strong and can bounce off your own lungs. Luckily, you can deflect it using the cigarette!

## Controls
  
| Action | Keyboard | Gamepad/Mobile |
| -------- | -------- | -------- |
| Move & Aim | Left & right arrow keys | Left & right d-pad buttons |
| Shoot Up | Up arrow key | Up d-pad button
| Attack | Spacebar | A (the bottom button) |

- Move in front of smoke to deflect it in the opposite direction. Smoke particles become smaller every time they bounce off anything other than the cigarette.
- Charge your attack (smoke) by holding the corresponding key, releasing to shoot. The longer you hold, the bigger your attack!
- If you are running the game locally, exit the game with the Esc key.

## Playing the Game
### Option 1: Play in Browser (Recommended)
You can simply click [here](https://panpov.github.io/magic-cigarette/) to play on your browser. It works on your phone too! No setup needed.
### Option 2: Run Locally
1. Pyxel requires **Python 3.10+** to work.
2. Install Pyxel via pip: ```pip install pyxel```
3. Clone the repository and run:
```
git clone https://github.com/panpov/magic-cigarette.git
cd magic-cigarette
python main.py
```
