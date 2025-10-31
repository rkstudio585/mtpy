# main.py

# ==============================================================================
# 1. SETUP & DEPENDENCY MANAGEMENT
# ==============================================================================

import sys
import subprocess
import importlib.util
from datetime import datetime # Needed for the new history viewer

REQUIRED_LIBRARIES = {
    'rich': 'rich', 'click': 'click', 'numpy': 'numpy',
    'PIL': 'Pillow', 'flask': 'Flask', 'pyfiglet': 'pyfiglet',
}

def check_and_install_dependencies():
    missing_libs = [pkg for mod, pkg in REQUIRED_LIBRARIES.items() if importlib.util.find_spec(mod) is None]
    if missing_libs:
        print(f"[-] Missing libraries: {', '.join(missing_libs)}")
        permission = input(f"[?] Install them now? (Y/n): ").lower().strip()
        if permission in ['y', 'yes', '']:
            print("[*] Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_libs])
                print("[+] Success! Please restart the script.")
                sys.exit(0)
            except subprocess.CalledProcessError as e:
                print(f"[!] Error: {e}"); sys.exit(1)
        else:
            print("[!] Cannot proceed without dependencies."); sys.exit(1)

check_and_install_dependencies()

# ==============================================================================
# 2. CORE IMPORTS & GLOBAL CONFIGURATION
# ==============================================================================

import os
import json
import random
import operator
import time
import uuid
from pathlib import Path

import click
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt
from rich.table import Table
from rich.text import Text
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, jsonify, request
from pyfiglet import Figlet

CACHE_DIR = Path.home() / ".cache"
DATA_FILE = CACHE_DIR / "mtpy-data.json"
API_KEY_FILE = CACHE_DIR / "mtpy-api.key"
CONSOLE = Console()

def generate_banner():
    figlet = Figlet(font='slant')
    banner_text = figlet.renderText('M T P Y')
    tagline = "A Math Game for Terminal Lovers"
    return f"{banner_text}\n{tagline.center(len(banner_text.splitlines()[1]))}"

# ==============================================================================
# 3. DATA MANAGEMENT
# ==============================================================================

def get_username(): return os.getenv('USER') or os.getenv('USERNAME') or 'Guest'

def initialize_data():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    user_data = {
        "username": get_username(), "rank": "Beginner", "total_score": 0,
        "min_score": None, "max_score": 0,
        "stats": {
            "total_correct": 0, "total_incorrect": 0, "total_played": 0,
            "easy_played": 0, "medium_played": 0, "hard_played": 0,
            "extreme_played": 0, "matrix_played": 0, "timed_played": 0,
            "survival_played": 0 # New stat for Survival Mode
        }, "history": []
    }
    save_data(user_data)
    api_key = str(uuid.uuid4()); save_api_key(api_key)
    return user_data, api_key

def load_data():
    if not DATA_FILE.exists() or not API_KEY_FILE.exists(): return initialize_data()
    try:
        with open(DATA_FILE, 'r') as f: user_data = json.load(f)
        # Backward compatibility check for new stats
        if 'survival_played' not in user_data['stats']: user_data['stats']['survival_played'] = 0
        with open(API_KEY_FILE, 'r') as f: api_key = f.read().strip()
        return user_data, api_key
    except (json.JSONDecodeError, FileNotFoundError): return initialize_data()

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)

def save_api_key(key):
    with open(API_KEY_FILE, 'w') as f: f.write(key)

def update_rank(data):
    # This function is unchanged
    score = data['total_score']
    if score > 5000: data['rank'] = "Math Grandmaster"
    elif score > 2000: data['rank'] = "Equation Wizard"
    elif score > 1000: data['rank'] = "Problem Pro"
    elif score > 500: data['rank'] = "Number Ninja"
    elif score > 100: data['rank'] = "Arithmetic Adept"
    else: data['rank'] = "Beginner"
    return data

# ==============================================================================
# 4. EXPRESSION GENERATION (Unchanged)
# ==============================================================================

def generate_expression(level):
    # This function is unchanged
    if level == 'easy':
        ops={'*':operator.mul,'/':operator.truediv,'+':operator.add,'-':operator.sub}
        op_sym = random.choice(list(ops.keys()))
        if op_sym == '/': n2 = random.randint(2,10); n1 = n2 * random.randint(2,10)
        else: n1,n2=random.randint(1,20),random.randint(1,20)
        return f"{n1} {op_sym} {n2}", float(ops[op_sym](n1,n2))
    elif level == 'medium':
        n1,n2,n3=random.randint(1,15),random.randint(1,15),random.randint(2,10)
        q = f"({n1} + {n2}) * {n3}"; return q, float(eval(q))
    elif level == 'hard':
        if random.choice([0,1]): b,e=random.randint(2,10),random.randint(2,3); return f"{b} ** {e}",float(b**e)
        else: r=random.randint(2,12); n=r**2; return f"sqrt({n})", float(r)
    elif level == 'extreme':
        import math; a=random.choice([30,45,60]); return f"sin({a})",round(math.sin(math.radians(a)),2)
    elif level == 'matrix':
        A,B=np.random.randint(0,10,(2,2)),np.random.randint(0,10,(2,2)); op=random.choice(['+','-','*'])
        if op=='+': ans=A+B
        elif op=='-': ans=A-B
        else: ans=np.dot(A,B)
        return (A,B,op),ans

# ==============================================================================
# 5. TUI & GAME LOGIC
# ==============================================================================

def display_header(user_data):
    # This function is unchanged
    CONSOLE.clear()
    CONSOLE.print(Panel(Text(generate_banner(), justify="center"), style="bold magenta", border_style="dim"))
    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column(style="bold cyan"); stats_table.add_column()
    stats_table.add_row("Username :", user_data['username'])
    stats_table.add_row("Rank :", user_data['rank'])
    stats_table.add_row("Score :", f"{user_data['total_score']:,}")
    stats_table.add_row("Success/Fail :", f"[green]{user_data['stats']['total_correct']}[/green] / [red]{user_data['stats']['total_incorrect']}[/red]")
    CONSOLE.print(Panel(stats_table, title="[bold]Player Info[/bold]", border_style="green"), justify="center")

def game_loop(level, user_data):
    # UPDATED: Now saves correct/incorrect counts to history
    session_score, session_correct, session_incorrect = 0, 0, 0
    display_header(user_data)
    CONSOLE.print(f"\n--- [bold yellow]{level.capitalize()} Mode[/bold yellow] ---", justify="center")
    CONSOLE.print("Type '[bold red]exit[/bold red]' to quit.", justify="center")
    while True:
        question, answer = generate_expression(level)
        try:
            if level == 'matrix':
                # Matrix logic remains the same
                A,B,op = question; CONSOLE.print(Panel(f"Solve:\n\n{A}\n\n {op}\n\n{B}", title="Matrix Problem"))
                r1=Prompt.ask("1st row"); r2=Prompt.ask("2nd row")
                if 'exit' in (r1.lower(), r2.lower()): break
                user_ans = np.array([[int(x) for x in r1.split()],[int(x) for x in r2.split()]])
                is_correct = np.array_equal(user_ans, answer)
            else:
                user_ans_str = Prompt.ask(f"[cyan]Q:[/cyan] {question} = ?")
                if user_ans_str.lower() == 'exit': break
                is_correct = (float(user_ans_str) == answer)
            
            if is_correct:
                CONSOLE.print("[green]Correct![/green] +10 pts\n"); session_score+=10; session_correct+=1; user_data['stats']['total_correct']+=1
            else:
                CONSOLE.print(f"[red]Incorrect.[/red] Answer was {answer}\n"); session_score-=5; session_incorrect+=1; user_data['stats']['total_incorrect']+=1
        except (ValueError, IndexError): CONSOLE.print("[red]Invalid input.[/red]\n")

    # Save session results
    user_data['total_score'] += session_score
    user_data['stats'][f"{level}_played"] += 1; user_data['stats']['total_played'] += 1
    if user_data['min_score'] is None or session_score < user_data['min_score']: user_data['min_score'] = session_score
    if session_score > user_data['max_score']: user_data['max_score'] = session_score
    # ENHANCED: Save correct/incorrect to history
    user_data['history'].append({'level': level, 'score': session_score, 'correct': session_correct, 'incorrect': session_incorrect, 'timestamp': time.time()})
    save_data(update_rank(user_data))
    Prompt.ask("\nPress Enter to return...")

def timed_game_loop(user_data):
    # UPDATED: Now saves correct/incorrect counts to history
    session_score, session_correct, session_incorrect = 0, 0, 0
    duration, start_time = 60, time.time()
    levels = ['easy', 'easy', 'medium', 'medium', 'hard']
    display_header(user_data); CONSOLE.print("\n--- [bold red]Timed Challenge![/bold red] ---", justify="center"); time.sleep(2)
    while (time.time() - start_time) < duration:
        level = random.choice(levels); question, answer = generate_expression(level)
        if level == 'matrix': continue
        try:
            q_start_time = time.time()
            user_answer_str = Prompt.ask(f"({level.capitalize()}) [cyan]Q:[/cyan] {question} = ?")
            if float(user_answer_str) == answer:
                points = max(1, 15 - int(time.time() - q_start_time))
                CONSOLE.print(f"[green]Correct![/green] +{points} pts\n"); session_score += points; session_correct += 1; user_data['stats']['total_correct'] += 1
            else:
                CONSOLE.print(f"[red]Incorrect.[/red] Ans: {answer}\n"); session_score -= 5; session_incorrect += 1; user_data['stats']['total_incorrect'] += 1
        except (ValueError, IndexError): CONSOLE.print("[red]Invalid input.[/red]\n")
        except Exception: break
    
    # Save session results
    user_data['total_score'] += session_score
    user_data['stats']['timed_played'] += 1; user_data['stats']['total_played'] += 1
    if user_data['min_score'] is None or session_score < user_data['min_score']: user_data['min_score'] = session_score
    if session_score > user_data['max_score']: user_data['max_score'] = session_score
    # ENHANCED: Save correct/incorrect to history
    user_data['history'].append({'level': 'timed', 'score': session_score, 'correct': session_correct, 'incorrect': session_incorrect, 'timestamp': time.time()})
    save_data(update_rank(user_data))
    Prompt.ask("\nPress Enter to return...")

def survival_game_loop(user_data):
    """
    NEW: A high-stakes game mode where one wrong answer ends the game.
    """
    score = 0 # In this mode, score is the number of correct answers.
    consecutive_correct = 0
    difficulty_levels = ['easy', 'medium', 'hard', 'extreme']
    
    display_header(user_data)
    CONSOLE.print("\n--- [bold purple]Survival Mode[/bold purple] ---", justify="center")
    CONSOLE.print("Difficulty increases every 3 correct answers. One mistake and it's over!", justify="center")
    time.sleep(2)

    while True:
        # Determine current difficulty
        level_index = min(consecutive_correct // 3, len(difficulty_levels) - 1)
        current_level = difficulty_levels[level_index]
        
        question, answer = generate_expression(current_level)
        
        CONSOLE.print(f"Score: [bold green]{score}[/bold green] | Level: [bold yellow]{current_level.capitalize()}[/bold yellow]", justify="right")
        
        try:
            user_answer_str = Prompt.ask(f"[cyan]Q:[/cyan] {question} = ?")
            if float(user_answer_str) == answer:
                score += 1
                consecutive_correct += 1
                CONSOLE.print(f"[bold green]Correct! Streak: {consecutive_correct}[/bold green]\n")
                # Check for level up
                if consecutive_correct % 3 == 0 and level_index < len(difficulty_levels) - 1:
                    CONSOLE.print(f"[bold yellow]LEVEL UP! Next level: {difficulty_levels[level_index + 1].capitalize()}[/bold yellow]")
            else:
                CONSOLE.print(f"\n[bold red]GAME OVER.[/bold red] The correct answer was [bold yellow]{answer}[/bold yellow].")
                CONSOLE.print(f"You achieved a final score of [bold green]{score}[/bold green] in Survival Mode!")
                break # Exit the loop on incorrect answer
        except (ValueError, IndexError):
            CONSOLE.print("\n[bold red]GAME OVER.[/bold red] Invalid input.")
            break
        except Exception:
            break

    # Save session results
    user_data['total_score'] += score # Add survival score to total score
    user_data['stats']['survival_played'] += 1
    user_data['stats']['total_played'] += 1
    user_data['stats']['total_correct'] += score
    user_data['stats']['total_incorrect'] += 1 # The one incorrect answer that ended the game
    if user_data['min_score'] is None or score < user_data['min_score']: user_data['min_score'] = score
    if score > user_data['max_score']: user_data['max_score'] = score
    user_data['history'].append({'level': 'survival', 'score': score, 'correct': score, 'incorrect': 1, 'timestamp': time.time()})
    save_data(update_rank(user_data))
    Prompt.ask("\nPress Enter to return to the main menu...")

def view_history(user_data):
    """
    NEW: Displays a table of the last 15 game sessions.
    """
    CONSOLE.clear()
    history = user_data.get('history', [])
    
    table = Table(title="[bold cyan]Last 15 Game Sessions[/bold cyan]", border_style="blue")
    table.add_column("Date", justify="center", style="cyan")
    table.add_column("Mode", justify="center", style="magenta")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Correct", justify="right", style="bright_green")
    table.add_column("Incorrect", justify="right", style="red")

    if not history:
        CONSOLE.print(Panel("[yellow]No history yet. Go play a game![/yellow]", title="Empty History"))
    else:
        # Get the last 15 entries and reverse them to show most recent first
        for session in reversed(history[-15:]):
            ts = datetime.fromtimestamp(session['timestamp']).strftime('%Y-%m-%d %H:%M')
            # Use .get() for backward compatibility with old history data
            correct = session.get('correct', 'N/A')
            incorrect = session.get('incorrect', 'N/A')
            table.add_row(
                ts,
                str(session['level']).capitalize(),
                str(session['score']),
                str(correct),
                str(incorrect)
            )
        CONSOLE.print(table)
    
    Prompt.ask("\nPress Enter to return to the main menu...")


def main_menu():
    """Main menu, now with Survival Mode and History Viewer."""
    user_data, _ = load_data()
    while True:
        display_header(user_data)
        menu = Table(title="Select a Mode", box=None, show_header=False)
        menu.add_column(style="bold"); menu.add_column()
        menu.add_row("[1]", "Easy"); menu.add_row("[2]", "Medium")
        menu.add_row("[3]", "Hard"); menu.add_row("[4]", "Extreme")
        menu.add_row("[5]", "Matrix")
        menu.add_row("[bold red][6][/bold red]", "Timed Challenge (60s)")
        menu.add_row("[bold purple][7][/bold purple]", "Survival Mode")
        menu.add_row("[cyan][8][/cyan]", "View History")
        menu.add_row("[9]", "Exit")
        
        CONSOLE.print(Panel(menu, border_style="blue"), justify="center")
        choice = Prompt.ask("Enter your choice", choices=[str(i) for i in range(1, 10)])
        
        level_map = {'1':'easy','2':'medium','3':'hard','4':'extreme','5':'matrix'}
        
        if choice in level_map:
            game_loop(level_map[choice], user_data); user_data, _ = load_data()
        elif choice == '6':
            timed_game_loop(user_data); user_data, _ = load_data()
        elif choice == '7':
            survival_game_loop(user_data); user_data, _ = load_data()
        elif choice == '8':
            view_history(user_data) # No need to reload data as it doesn't change
        elif choice == '9':
            CONSOLE.print("[bold cyan]Thanks for playing MTPY![/bold cyan]"); break

# ==============================================================================
# 6. CLI COMMANDS (Unchanged)
# ==============================================================================

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """MTPY: A Math Game for Terminal Lovers."""
    if ctx.invoked_subcommand is None: main_menu()

@cli.command()
def status():
    """Generates a social media shareable status card image."""
    # This function is unchanged from the previous version.
    CONSOLE.print("[*] Generating status card...")
    user_data, _ = load_data()
    width, height = 1200, 630
    bg_color, text_color = (15,23,42), (226,232,240)
    accent1, accent2 = (56,189,248), (163,230,53)
    line_color = (51,65,85)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font_b = "arialbd.ttf" if sys.platform == "win32" else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_r = "arial.ttf" if sys.platform == "win32" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        title_font = ImageFont.truetype(font_b, 80); subtitle_font = ImageFont.truetype(font_r, 32)
        text_font = ImageFont.truetype(font_r, 28); value_font = ImageFont.truetype(font_b, 28)
    except IOError:
        title_font, subtitle_font, text_font, value_font = [ImageFont.load_default()]*4
    draw.text((60,40), "MTPY Game", font=title_font, fill=accent1)
    draw.text((65,130), "Player Status Card", font=subtitle_font, fill=text_color)
    draw.line([(60,180),(width-60,180)], fill=line_color, width=3)
    y_pos, x_keys, x_vals, line_h = 220, 60, 600, 55
    stats = {
        "Player": user_data.get('username','N/A'),
        "Rank": user_data.get('rank','N/A'),
        "Total Score": f"{user_data.get('total_score',0):,}",
        "Survival Best": user_data.get('stats',{}).get('survival_played',0),
        "Correct / Incorrect": f"{user_data.get('stats',{}).get('total_correct',0)} / {user_data.get('stats',{}).get('total_incorrect',0)}",
        "Highest Session Score": user_data.get('max_score',0),
    }
    for k, v in stats.items():
        draw.text((x_keys, y_pos), f"{k}:", font=text_font, fill=text_color)
        draw.text((x_vals, y_pos), str(v), font=value_font, fill=accent2)
        y_pos += line_h
    output_filename = "mtpy_status.png"
    img.save(output_filename)
    CONSOLE.print(f"[green]Success![/green] Card saved as [cyan]{output_filename}[/cyan]")

@cli.command()
def share():
    """Starts a local API server to share your game data."""
    # This function is unchanged.
    user_data, api_key = load_data()
    app = Flask(__name__)
    @app.route('/api')
    def share_data():
        if request.args.get('key') == api_key: return jsonify(user_data)
        else: return jsonify({"error": "Invalid API key"}), 401
    CONSOLE.print(Panel(f"API Server running!\nKey: [yellow]{api_key}[/yellow]\nURL: [cyan]http://127.0.0.1:5000/api?key={api_key}[/cyan]\n\nPress CTRL+C to stop.", title="[green]Share Server[/green]"))
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==============================================================================
# 7. SCRIPT ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        CONSOLE.print("\n[bold yellow]Game interrupted. Exiting.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        CONSOLE.print(Panel(f"[bold red]An unexpected error occurred:[/bold red]\n{e}", title="[bold red]Error[/bold red]"))
        sys.exit(1)
