# Kivy Catch Game

A visually enhanced, addictive catch game built with Python and Kivy. Move your paddle to catch falling balls, rack up combos, collect power-ups, and challenge your high score! Designed for both desktop and touch devices.

---

## Features

- **Smooth Controls:** Drag or swipe to move the paddle.
- **Combo System:** Consecutive catches increase your score multiplier.
- **Power-Ups:** Collect slow motion, double points, extra life, and paddle size changes.
- **Health Bar:** Misses are shown as a health bar below the score.
- **Persistent High Score:** Your best score is saved between sessions.
- **Visual Effects:** Particle trails, glowing ball, paddle flash, and animated starfield background.
- **Pause/Resume:** Pause the game at any time.
- **Mobile-Friendly:** Fixed portrait window for easy play on touch devices.
- **Extensible:** Clean codebase for adding new features or power-ups.

---

## Screenshots

<p align="center">
  <img src="Screenshots/Screenshot.png" alt="Game Screenshot 1" width="300"/>
  <img src="Screenshots/Screenshot2.png" alt="Game Screenshot 2" width="300"/>
</p>

---

## How to Run

1. **Install dependencies:**
    ```sh
    pip install kivy
    ```
2. **Run the game:**
    ```sh
    python main.py
    ```

---

## How to Build as Windows EXE

1. **Install PyInstaller:**
    ```sh
    pip install pyinstaller
    ```
2. **Build:**
    ```sh
    pyinstaller --onefile --noconsole main.py
    ```
3. **Copy assets** (`catch.wav`, `miss.wav`, `startup.wav`, `gameover.wav`, `highscore.txt`) to the `dist` folder if needed.

---

## Repository Structure

```
CatchGame/
├── main.py
├── catch.wav
├── miss.wav
├── startup.wav
├── gameover.wav
├── highscore.txt
├── README.md
├── LICENSE
└── Screenshots/
    ├── Screenshot.png
    └── Screenshot2.png
```

---

## Credits

- **Game & Code:** Gwen
- **Framework:** [Kivy](https://kivy.org/)

---

## License

MIT License

---

Enjoy the game! 🚀
