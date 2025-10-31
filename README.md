# MTPY - A Math Game for the Terminal

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/rkstudio585/mtpy)](https://github.com/rkstudio585/mtpy/issues)
[![GitHub forks](https://img.shields.io/github/forks/rkstudio585/mtpy)](https://github.com/rkstudio585/mtpy/network)
[![GitHub stars](https://img.shields.io/github/stars/rkstudio585/mtpy)](https://github.com/rkstudio585/mtpy/stargazers)

Welcome to **MTPY**, a feature-rich, command-line math game designed to make learning and practicing math fun, fast, and engaging, all from the comfort of your terminal.

Built with the powerful **Rich** library, MTPY provides a beautiful and user-friendly Text-based User Interface (TUI) that's perfect for students, developers, and anyone who loves the command line.


*(Note: This is a representative GIF. You can create one for your project using a tool like `asciinema` and `agg`)*

---

## ✨ Features

-   **Multiple Game Modes:**
    -   **Classic Mode:** Choose your difficulty and play at your own pace.
    -   **Timed Challenge:** Race against the clock to solve as many problems as you can in 60 seconds.
    -   **Survival Mode:** A high-stakes mode where one wrong answer ends the game!
-   **Five Difficulty Levels:**
    -   **Easy:** Basic arithmetic (`+`, `-`, `×`, `÷`).
    -   **Medium:** Operations with parentheses.
    -   **Hard:** Exponents and square roots.
    -   **Extreme:** Basic trigonometry.
    -   **Matrix:** 2x2 matrix addition, subtraction, and multiplication.
-   **Beautiful & Modern TUI:** A clean, colorful, and intuitive interface powered by `rich`.
-   **Persistent Player Stats:** All your progress, scores, and game history are automatically saved to `~/.cache/mtpy-data.json`.
-   **In-Game History Viewer:** Track your progress by viewing a table of your last 15 game sessions directly within the game.
-   **Shareable Status Card:** Generate a stylish PNG image of your stats, perfect for sharing on social media.
-   **API for Data Sharing:** Start a local Flask server to share your game data securely via a unique API key.
-   **Automatic Dependency Management:** The script checks for required libraries and offers to install them for you on the first run.

---

## 🚀 Installation

Getting `mtpy` up and running is simple. You just need Python 3.8+ and `git` installed.

**1. Clone the Repository:**
Open your terminal and clone the repository to your local machine.
```bash
git clone https://github.com/rkstudio585/mtpy.git
```

**2. Navigate to the Project Directory:**
```bash
cd mtpy
```

**3. (Recommended) Create a Virtual Environment:**
Using a virtual environment is best practice to keep project dependencies isolated.
```bash
# For Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.\.venv\Scripts\activate
```

**4. Run the Script:**
That's it! Just run `main.py`.
```bash
python main.py
```
The first time you run the script, it will automatically detect any missing libraries (like `rich`, `click`, etc.) and ask for your permission to install them. Just type `y` and press Enter. After the installation, you will be prompted to restart the script.

---

## 🎮 How to Play

### Starting the Game

To launch the game and see the main menu, simply run:
```bash
python main.py
```

### Command-Line Arguments

MTPY also comes with powerful command-line arguments for extra features.

#### `status`: Generate a Status Card

This command creates a beautiful, shareable image named `mtpy_status.png` in the project directory, summarizing your player rank, score, and other stats.

```bash
python main.py status
```

*(This is an example image. Yours will reflect your own stats.)*

#### `share`: Share Your Stats via API

This command starts a local web server, allowing you to access your complete game data in JSON format through a secure API endpoint.

```bash
python main.py share
```

The server will provide you with a unique API key. You can then access your data using a tool like `curl` or by visiting the URL in a browser:
```bash
# Example curl request
curl http://127.0.0.1:5000/api?key=YOUR_UNIQUE_API_KEY_HERE
```
Press `CTRL+C` in the terminal to stop the server.

---

## 🔧 How It Works

MTPY is a single-file Python application that leverages several powerful open-source libraries:

-   **Core Logic:** All game logic, data management, and user interaction are contained within `main.py`.
-   **TUI (Text-based User Interface):** [**Rich**](https://github.com/Textualize/rich) is used for rendering beautiful tables, panels, prompts, and styled text in the terminal.
-   **CLI (Command-Line Interface):** [**Click**](https://click.palletsprojects.com/) handles the creation of the robust command-line arguments (`--status`, `--share`).
-   **Data Storage:** Player progress is stored in a human-readable JSON file (`mtpy-data.json`) located in the user's home cache directory (`~/.cache/`).
-   **Image Generation:** [**Pillow**](https://python-pillow.org/) (PIL Fork) is used to dynamically create the `mtpy_status.png` image with your stats.
-   **API Server:** A lightweight [**Flask**](https://flask.palletsprojects.com/) web server provides the `/api` endpoint for data sharing.
-   **Math Engine:** Python's built-in `operator` module and [**NumPy**](https://numpy.org/) (for matrix math) are used to generate and evaluate mathematical expressions.
-   **Banner Text:** [**PyFiglet**](https://github.com/pwaller/pyfiglet) is used to generate the cool ASCII art banner on the home screen.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  **Fork the Project**
2.  **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3.  **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4.  **Push to the Branch** (`git push origin feature/AmazingFeature`)
5.  **Open a Pull Request**

Don't forget to give the project a star! Thanks again!

## 📜 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.
