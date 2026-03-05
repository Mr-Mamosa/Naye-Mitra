import curses
import textwrap
import time
import threading
from engine import QueryEngine

# -------------------------------
# Utility Functions
# -------------------------------

def draw_centered(stdscr, y, text, color_pair=0, bold=False):
    """Draws a string centered horizontally on a specific row."""
    height, width = stdscr.getmaxyx()
    x = max(0, (width - len(text)) // 2)
    attr = curses.color_pair(color_pair)
    if bold:
        attr |= curses.A_BOLD
    if 0 <= y < height:
        stdscr.addnstr(y, x, text, width - x - 1, attr)

def loading_animation(stdscr, stop_event):
    """Spinner that runs in a thread to show the AI is working."""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        height, width = stdscr.getmaxyx()
        # Position the loader slightly above the input line
        y = height - 5
        loading_text = f"{chars[i % len(chars)]} Searching Legal Database..."
        draw_centered(stdscr, y, loading_text, 6)
        stdscr.refresh()
        time.sleep(0.1)
        i += 1

def draw_main_title(stdscr, height, width):
    title_text = [
        " __        __   _                            ",
        " \\ \\      / /__| | ___ ___  _ __ ___   ___  ",
        "  \\ \\ /\\ / / _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\ ",
        "   \\ V  V /  __/ | (_| (_) | | | | | |  __/ ",
        "    \\_/\\_/ \\___|_|\\___\\___/|_| |_| |_|\\___| ",
        "",
        "             A Law AI Advisor               "
    ]
    if height < 15:
        return
    title_y = height // 2 - len(title_text) // 2 - 4
    for i, line in enumerate(title_text):
        draw_centered(stdscr, title_y + i, line, 7)

def draw_footer(stdscr, height, width):
    footer_text = " Type your query and press ENTER | 'exit' to quit "
    if height > 2:
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height - 1, 0, (" " * (width - 1))[:width-1])
        stdscr.addnstr(height - 1, max(0, (width - len(footer_text)) // 2), footer_text, width - 1)
        stdscr.attroff(curses.color_pair(3))

def wrap_text(text, width):
    return textwrap.wrap(text, width)

# -------------------------------
# Main Application
# -------------------------------

def main(stdscr):
    curses.curs_set(1)
    stdscr.nodelay(False)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # AI Answer
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # User Query
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)     # Footer
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Low Risk
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)      # High Risk
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Loading/Status
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Title

    try:
        engine = QueryEngine()
    except Exception as e:
        stdscr.addstr(0, 0, f"Engine Error: {str(e)[:50]}")
        stdscr.refresh()
        stdscr.getch()
        return

    # chat_history stores structured dicts: {'user': str, 'ai': str, 'conf': float, 'status': str}
    chat_history = []
    input_buffer = ""

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if width < 40 or height < 10:
            stdscr.addstr(0, 0, "Please enlarge terminal.")
            stdscr.refresh()
            time.sleep(1)
            continue

        draw_footer(stdscr, height, width)

        if not chat_history:
            draw_main_title(stdscr, height, width)
            input_y = height // 2 + 5
        else:
            # Layout for active chat: focus on the latest response
            last_chat = chat_history[-1]
            y_offset = 2

            # Draw User Query (Centered)
            draw_centered(stdscr, y_offset, f"❯ {last_chat['user']}", 2, bold=True)
            y_offset += 2

            # Draw AI Answer (Centered & Wrapped)
            ai_lines = wrap_text(last_chat['ai'], width - 10)
            for line in ai_lines:
                if y_offset < height - 7:
                    draw_centered(stdscr, y_offset, line, 1)
                    y_offset += 1

            # Draw Veracity Badge
            y_offset += 1
            status = last_chat['status']
            v_color = 5 if "🔴" in status else 6 if "🟡" in status else 4
            badge = f"📊 Confidence: {last_chat['conf']:.2f}% | {status}"
            draw_centered(stdscr, y_offset, badge, v_color, bold=True)

            input_y = height - 3

        # Draw Search Bar
        search_prompt = f"SEARCH: {input_buffer}"
        draw_centered(stdscr, input_y, search_prompt, 2)

        # Place cursor at the end of input
        cursor_x = (width + len(search_prompt)) // 2
        stdscr.move(input_y, min(cursor_x, width - 1))

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_BACKSPACE, 127, 8):
            input_buffer = input_buffer[:-1]
        elif key in (curses.KEY_ENTER, 10, 13):
            query = input_buffer.strip()
            if query.lower() in ["exit", "quit"]:
                break
            if not query:
                continue

            input_buffer = ""

            # Animation Handling
            stop_event = threading.Event()
            animation_thread = threading.Thread(target=loading_animation, args=(stdscr, stop_event))
            animation_thread.start()

            # Process Query
            try:
                result = engine.ask(query)
            finally:
                stop_event.set()
                animation_thread.join()

            chat_history.append({
                'user': query,
                'ai': result.get("answer", "No response generated."),
                'conf': result.get("confidence", 0),
                'status': result.get("status", "Unknown")
            })

        elif 32 <= key <= 126:
            input_buffer += chr(key)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
