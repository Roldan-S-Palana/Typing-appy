import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import time
import json
import os

class TypingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Test App")
        self.root.geometry("800x600")

        # Default theme
        self.current_theme = {
            'bg': '#f8f9fa',
            'fg': '#212529',
            'text_bg': '#ffffff',
            'text_fg': '#495057',
            'button_bg': '#007bff',
            'button_fg': '#ffffff',
            'error_color': '#dc3545',
            'correct_color': '#28a745',
            'font': ('Segoe UI', 12)
        }

        # Load themes if available
        self.themes = self.load_themes()

        # Sample text for typing test
        self.sample_text = "The quick brown fox jumps over the lazy dog. This is a sample text for the typing test. Practice makes perfect when learning to type faster and more accurately."

        # Difficulty levels
        self.difficulty = 0  # 0: basic, 1: intermediate, 2: advanced

        # Variables
        self.start_time = None
        self.timer_running = False
        self.test_duration = 60  # Default 1 minute in seconds
        self.user_input = tk.StringVar()
        self.wpm = 0
        self.accuracy = 0
        self.total_words_typed = 0  # Track total words across all texts
        self.total_correct_chars = 0  # Track total correct characters
        self.total_chars_typed = 0  # Track total characters typed

        self.setup_ui()

        self.input_entry.focus()

        # Initialize with basic difficulty text
        self.reset_sample_text()

    def setup_ui(self):
        # Menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        theme_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Themes", menu=theme_menu)
        for theme_name in self.themes:
            theme_menu.add_command(label=theme_name, command=lambda t=theme_name: self.apply_theme(t))

        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Customize Theme", command=self.customize_theme)

        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.current_theme['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Text display with colored text
        self.text_frame = tk.Frame(self.main_frame, bg=self.current_theme['text_bg'], bd=2, relief='groove')
        self.text_frame.pack(pady=25, padx=25, fill=tk.X)

        # Create text widget for multi-line display with scrolling
        self.text_widget = tk.Text(self.text_frame, wrap=tk.WORD, font=('Segoe UI', 16),
                                  bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'],
                                  bd=2, highlightthickness=1, relief='sunken', padx=15, pady=15, spacing1=2, spacing2=2, spacing3=2,
                                  height=4)  # Further reduced height for more compact display
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(state=tk.DISABLED)  # Make it read-only

        self.update_colored_text()

        # Input field
        self.input_entry = tk.Entry(self.main_frame, textvariable=self.user_input, font=('Segoe UI', 14),
                                     bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'],
                                     bd=2, relief='sunken', insertwidth=2)
        self.input_entry.pack(fill=tk.X, padx=30, pady=15)
        self.input_entry.bind('<KeyRelease>', self.check_input)
        self.input_entry.bind('<Tab>', self.restart_test)

        # Stats frame (initially hidden)
        self.stats_frame = tk.Frame(self.main_frame, bg=self.current_theme['bg'], bd=1, relief='solid')

        self.wpm_label = tk.Label(self.stats_frame, text="", bg=self.current_theme['bg'], fg=self.current_theme['fg'],
                                   font=('Segoe UI', 14, 'bold'))

        self.accuracy_label = tk.Label(self.stats_frame, text="", bg=self.current_theme['bg'], fg=self.current_theme['fg'],
                                        font=('Segoe UI', 14, 'bold'))

        # Buttons
        self.button_frame = tk.Frame(self.main_frame, bg=self.current_theme['bg'])
        self.button_frame.pack(pady=25)

        self.start_button = tk.Button(self.button_frame, text="Start Test", command=self.start_test,
                                       bg=self.current_theme['button_bg'], fg=self.current_theme['button_fg'],
                                       font=('Segoe UI', 12, 'bold'), relief='raised', bd=2, padx=20, pady=8)
        self.start_button.pack(side=tk.LEFT, padx=15)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_test,
                                       bg=self.current_theme['button_bg'], fg=self.current_theme['button_fg'],
                                       font=('Segoe UI', 12, 'bold'), relief='raised', bd=2, padx=20, pady=8)
        self.reset_button.pack(side=tk.LEFT, padx=15)

        # Difficulty and Duration selectors
        options_frame = tk.Frame(self.main_frame, bg=self.current_theme['bg'])
        options_frame.pack(pady=15)

        # Difficulty selector
        difficulty_frame = tk.Frame(options_frame, bg=self.current_theme['bg'], bd=1, relief='ridge')
        difficulty_frame.pack(side=tk.LEFT, padx=15)

        tk.Label(difficulty_frame, text="Difficulty:", bg=self.current_theme['bg'], fg=self.current_theme['fg'],
                  font=('Segoe UI', 11, 'bold')).pack(side=tk.TOP, padx=8, pady=5)

        self.difficulty_var = tk.StringVar(value="Basic")
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var,
                                         values=["Basic", "Intermediate", "Advanced"], state="readonly", width=14,
                                         font=('Segoe UI', 10))
        difficulty_combo.pack(side=tk.TOP, padx=8, pady=5)
        difficulty_combo.bind('<<ComboboxSelected>>', self.change_difficulty)

        # Duration selector
        duration_frame = tk.Frame(options_frame, bg=self.current_theme['bg'], bd=1, relief='ridge')
        duration_frame.pack(side=tk.LEFT, padx=15)

        tk.Label(duration_frame, text="Duration:", bg=self.current_theme['bg'], fg=self.current_theme['fg'],
                  font=('Segoe UI', 11, 'bold')).pack(side=tk.TOP, padx=8, pady=5)

        self.duration_var = tk.StringVar(value="1 min")
        duration_combo = ttk.Combobox(duration_frame, textvariable=self.duration_var,
                                       values=["30 sec", "1 min", "2 min", "3 min", "5 min"], state="readonly", width=10,
                                       font=('Segoe UI', 10))
        duration_combo.pack(side=tk.TOP, padx=8, pady=5)
        duration_combo.bind('<<ComboboxSelected>>', self.change_duration)

        # Force update to ensure widgets are visible
        self.root.update_idletasks()

        # Countdown/Timer label
        self.timer_label = tk.Label(self.main_frame, text="Ready to start!", bg=self.current_theme['bg'], fg=self.current_theme['fg'],
                                     font=('Segoe UI', 18, 'bold'))
        self.timer_label.pack(pady=15)

    def load_themes(self):
        themes_file = 'themes.json'
        if os.path.exists(themes_file):
            with open(themes_file, 'r') as f:
                return json.load(f)
        else:
            # Default themes
            return {
                'Light': {
                    'bg': '#f0f0f0',
                    'fg': '#000000',
                    'text_bg': '#ffffff',
                    'text_fg': '#000000',
                    'button_bg': '#e0e0e0',
                    'button_fg': '#000000',
                    'error_color': '#ff0000',
                    'correct_color': '#00aa00',
                    'font': ('Arial', 12)
                },
                'Dark': {
                    'bg': '#2e2e2e',
                    'fg': '#ffffff',
                    'text_bg': '#3e3e3e',
                    'text_fg': '#ffffff',
                    'button_bg': '#4e4e4e',
                    'button_fg': '#ffffff',
                    'error_color': '#ff6b6b',
                    'correct_color': '#51cf66',
                    'font': ('Arial', 12)
                }
            }

    def apply_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            self.update_ui_theme()

    def update_ui_theme(self):
        self.root.configure(bg=self.current_theme['bg'])
        self.main_frame.configure(bg=self.current_theme['bg'])
        self.text_frame.configure(bg=self.current_theme['text_bg'])
        self.text_widget.configure(bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'])
        # Update text widget tags
        self.text_widget.tag_configure("correct", foreground=self.current_theme.get('correct_color', '#00aa00'), underline=True)
        self.text_widget.tag_configure("error", foreground=self.current_theme.get('error_color', '#ff0000'), underline=True)
        self.text_widget.tag_configure("normal", foreground=self.current_theme['text_fg'])
        self.input_entry.configure(bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'], font=self.current_theme['font'])
        self.stats_frame.configure(bg=self.current_theme['bg'])
        self.wpm_label.configure(bg=self.current_theme['bg'], fg=self.current_theme['fg'], font=self.current_theme['font'])
        self.accuracy_label.configure(bg=self.current_theme['bg'], fg=self.current_theme['fg'], font=self.current_theme['font'])
        self.button_frame.configure(bg=self.current_theme['bg'])
        self.start_button.configure(bg=self.current_theme['button_bg'], fg=self.current_theme['button_fg'], font=self.current_theme['font'])
        self.reset_button.configure(bg=self.current_theme['button_bg'], fg=self.current_theme['button_fg'], font=self.current_theme['font'])
        self.timer_label.configure(bg=self.current_theme['bg'], fg=self.current_theme['fg'], font=self.current_theme['font'])
        # Update menu bar colors (limited support in Tkinter)
        try:
            self.menubar.configure(bg=self.current_theme.get('menu_bg', self.current_theme['bg']))
            # Try to update individual menu items
            for i in range(self.menubar.index('end') + 1):
                try:
                    menu = self.menubar.entrycget(i, 'menu')
                    if menu:
                        menu.configure(bg=self.current_theme.get('menu_bg', self.current_theme['bg']))
                except:
                    pass
        except:
            pass  # Menu colors may not be fully customizable on all platforms

    def customize_theme(self):
        # Simple customization dialog
        customize_window = tk.Toplevel(self.root)
        customize_window.title("Customize Theme")
        customize_window.geometry("500x600")

        # Color entries and picker buttons
        color_entries = {}

        def create_color_picker(label_text, key, default_value):
            frame = tk.Frame(customize_window)
            frame.pack(pady=5)

            tk.Label(frame, text=label_text).pack(side=tk.LEFT)

            entry = tk.Entry(frame, width=20)
            entry.insert(0, self.current_theme.get(key, default_value))
            entry.pack(side=tk.LEFT, padx=5)

            def pick_color():
                color = colorchooser.askcolor(title=f"Choose {label_text}")[1]
                if color:
                    entry.delete(0, tk.END)
                    entry.insert(0, color)

            tk.Button(frame, text="Pick Color", command=pick_color).pack(side=tk.LEFT)

            color_entries[key] = entry

        create_color_picker("Background Color:", 'bg', self.current_theme['bg'])
        create_color_picker("Foreground Color:", 'fg', self.current_theme['fg'])
        create_color_picker("Text Background Color:", 'text_bg', self.current_theme['text_bg'])
        create_color_picker("Text Foreground Color:", 'text_fg', self.current_theme['text_fg'])
        create_color_picker("Button Background Color:", 'button_bg', self.current_theme['button_bg'])
        create_color_picker("Button Foreground Color:", 'button_fg', self.current_theme['button_fg'])
        create_color_picker("Menu Bar Background Color:", 'menu_bg', self.current_theme.get('menu_bg', self.current_theme['bg']))
        create_color_picker("Error Color:", 'error_color', self.current_theme.get('error_color', '#ff0000'))
        create_color_picker("Correct Color:", 'correct_color', self.current_theme.get('correct_color', '#00aa00'))

        def save_custom_theme():
            for key, entry in color_entries.items():
                self.current_theme[key] = entry.get()
            self.update_ui_theme()
            self.save_themes()
            customize_window.destroy()

        tk.Button(customize_window, text="Save", command=save_custom_theme).pack(pady=20)

    def save_themes(self):
        with open('themes.json', 'w') as f:
            json.dump(self.themes, f)

    def update_colored_text(self):
        # Clear and update text widget
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)

        user_text = self.user_input.get()
        sample_text = self.sample_text

        # Configure tags for coloring with more visible styling
        self.text_widget.tag_configure("correct",
                                      foreground=self.current_theme.get('correct_color', '#28a745'),
                                      background='#d4edda',  # Light green background
                                      font=('Segoe UI', 16, 'bold'))
        self.text_widget.tag_configure("error",
                                      foreground=self.current_theme.get('error_color', '#dc3545'),
                                      background='#f8d7da',  # Light red background
                                      font=('Segoe UI', 16, 'bold'), overstrike=True)
        self.text_widget.tag_configure("normal",
                                      foreground=self.current_theme['text_fg'],
                                      font=('Segoe UI', 16))

        # Insert text with appropriate tags
        for i, char in enumerate(sample_text):
            if i < len(user_text):
                # Character has been typed
                if user_text[i] == char:
                    # Correct character
                    tag = "correct"
                else:
                    # Incorrect character
                    tag = "error"
            else:
                # Character not yet typed
                tag = "normal"

            self.text_widget.insert(tk.END, char, tag)

        self.text_widget.config(state=tk.DISABLED)

        # Auto-scroll to show upcoming text (next 100 characters)
        if user_text:
            # Find the current character position in the text
            char_index = len(user_text) + 50  # Look ahead 50 characters
            if char_index < len(sample_text):
                # Convert character index to line.char format for Text widget
                line_char = self.text_widget.index(f"1.0 + {char_index} chars")
                # Scroll to keep upcoming text visible
                self.text_widget.see(line_char)
            else:
                # If near the end, make sure the end is visible
                self.text_widget.see(tk.END)

        # Force update to make sure changes are visible
        self.text_widget.update_idletasks()

    def start_test(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.input_entry.focus()
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = time.time() - self.start_time
            remaining = max(0, self.test_duration - elapsed)

            if remaining <= 0:
                # Add any remaining typed text to totals before ending
                self.add_current_text_to_totals()
                self.end_test()
            else:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                self.timer_label.config(text=f"Time: {minutes}:{seconds:02d}")
                self.root.after(100, self.update_timer)

    def check_input(self, event):
        user_text = self.user_input.get()

        # Auto-start timer when user starts typing
        if not self.timer_running and user_text.strip():
            self.start_test()

        if self.timer_running:
            self.calculate_stats(user_text)

        # Update colored text on every keystroke
        self.update_colored_text()

        # Check if user has completed the entire text
        # Only end test if timer is running (user actually started typing)
        if len(user_text) >= len(self.sample_text) and self.timer_running:
            # Add final text stats to totals
            self.add_current_text_to_totals()
            self.end_test()

    def calculate_stats(self, user_text):
        # This method is kept for compatibility but stats are now accumulated in add_current_text_to_totals
        pass

    def add_current_text_to_totals(self):
        user_text = self.user_input.get()
        if user_text:
            # Add words from current text to total
            words_in_current_text = len(user_text.split())
            self.total_words_typed += words_in_current_text

            # Add correct characters from current text to total
            correct_chars = sum(1 for a, b in zip(user_text, self.sample_text) if a == b)
            self.total_correct_chars += correct_chars
            self.total_chars_typed += len(user_text)

    def end_test(self):
        # Time's up - end the test (no more loading new texts since we show all at once)
        self.timer_running = False

        # Calculate final stats based on total accumulated stats
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.wpm = int(self.total_words_typed / (elapsed_time / 60)) if elapsed_time > 0 else 0
            self.accuracy = int((self.total_correct_chars / self.total_chars_typed) * 100) if self.total_chars_typed > 0 else 0

            # Show results
            self.stats_frame.pack(pady=10)
            self.wpm_label.config(text=f"WPM: {self.wpm}")
            self.wpm_label.pack(side=tk.LEFT, padx=10)
            self.accuracy_label.config(text=f"Accuracy: {self.accuracy}%")
            self.accuracy_label.pack(side=tk.LEFT, padx=10)

            # Disable input
            self.input_entry.config(state='disabled')

            # Prevent multiple message boxes
            if not hasattr(self, 'test_completed') or not self.test_completed:
                self.test_completed = True
                messagebox.showinfo("Test Complete", f"Final Results:\nWPM: {self.wpm}\nAccuracy: {self.accuracy}%\nTotal words typed: {self.total_words_typed}")

                # Prepare for next test: shuffle text and re-enable input
                self.reset_sample_text(shuffle=True)
                self.input_entry.config(state='normal')
                self.test_completed = False

    def change_difficulty(self, event=None):
        difficulty_map = {"Basic": 0, "Intermediate": 1, "Advanced": 2}
        self.difficulty = difficulty_map[self.difficulty_var.get()]
        self.reset_sample_text()

    def change_duration(self, event=None):
        duration_map = {"30 sec": 30, "1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300}
        self.test_duration = duration_map[self.duration_var.get()]

    def restart_test(self, event=None):
        """Restart the test with shuffled passages if test is ongoing"""
        if self.timer_running:
            # Reset all test variables
            self.timer_running = False
            self.start_time = None
            self.user_input.set("")
            self.wpm = 0
            self.accuracy = 0
            self.total_words_typed = 0
            self.total_correct_chars = 0
            self.total_chars_typed = 0
            self.test_completed = False

            # Hide stats frame
            self.stats_frame.pack_forget()
            self.timer_label.config(text="Ready to start!")

            # Generate new shuffled sample text
            self.reset_sample_text(shuffle=True)

            # Re-enable input
            self.input_entry.config(state='normal')
            self.input_entry.focus()

        return "break"  # Prevent default tab behavior

    def reset_sample_text(self, event=None, shuffle=False):
        # Generate concatenated sample text with all available passages for the difficulty
        import random
        import string

        if self.difficulty == 0:  # Basic
            sample_texts = [
                "The slash (/) is a versatile mark used to indicate options (and/or), represent fractions (1/2), and separate lines of poetry. It's a simple yet effective way to convey multiple choices or alternatives within a single line of text.",
                "A virtual assistant (typically abbreviated to VA) is generally self-employed and provides professional administrative, technical, or creative assistance to clients remotely from a home office.",
                "Typists often handle confidential documents. Treat sensitive information with the utmost care. Follow company policies regarding data security and privacy. Securely store or destroy confidential documents as instructed.",
                "Familiarity with word processing, spreadsheet, and presentation software is essential for most typing jobs. Additionally, learning to use specialized software like transcription or dictation programs can expand your career opportunities.",
                "A teacher's professional duties may extend beyond formal teaching. Outside of the classroom teachers may accompany students on field trips, supervise study halls, help with the organization of school functions, and serve as supervisors for extracurricular activities. In some education systems, teachers may have responsibility for student discipline.",
                "The quick brown fox jumps over the lazy dog. This is a sample text for the typing test. Practice makes perfect when learning to type faster and more accurately.",
                "Pack my box with five dozen liquor jugs. How vexingly quick daft zebras jump! Bright vixens jump; dozy fowl quack. Sphinx of black quartz, judge my vow.",
                "The five boxing wizards jump quickly. Jackdaws love my big sphinx of quartz. The jay, pig, fox, zebra, and my wolves quack! Blowzy night-frumps vex'd Jack Q.",
                "Quick zephyrs blow, vexing daft Jim. Two driven jocks help fax my big quiz. Five quacking zephyrs jolt my wax bed. The lazy major was fixing Cupid's broken quiver.",
                "Crazy Fredrick bought many very exquisite opal jewels."
            ]
            if shuffle:
                random.shuffle(sample_texts)
            self.sample_text = " ".join(sample_texts)

        elif self.difficulty == 1:  # Intermediate
            # Add numbers and some special characters
            base_texts = [
                "Investing is a powerful strategy for building wealth over the long term. It involves putting your money to work in assets that have the potential to increase in value over time, such as stocks, bonds, real estate, or mutual funds. While investing comes with risks, it also offers the opportunity to earn substantial returns, outpacing inflation and growing your wealth significantly over the years. However, successful investing requires careful planning, research, and a long-term perspective. It's important to understand your risk tolerance, diversify your investments, and avoid making impulsive decisions based on short-term market fluctuations. By starting early and investing consistently, you can harness the power of compound interest, where your earnings generate more earnings, accelerating your wealth accumulation over time.",
                "The fastest typing speed ever, 216 words per minute, was achieved by Stella Pajunas-Garnand from Chicago in 1946 in one minute on an IBM electric. As of 2005, writer Barbara Blackburn was the fastest English language typist in the world, according to The Guinness Book of World Records. Using the Dvorak Simplified Keyboard, she had maintained 150 wpm for 50 minutes, and 170 wpm for shorter periods, with a peak speed of 212 wpm. Blackburn, who failed her QWERTY typing class in high school, first encountered the Dvorak keyboard in 1938, quickly learned to achieve very high speeds, and occasionally toured giving speed-typing demonstrations during her secretarial career. She appeared on Late Night with David Letterman on January 24, 1985, but felt that Letterman made a spectacle of her. Blackburn died in April 2008. (Wikipedia)",
                "In 2010, the US Government Accountability Office (GAO) found that 92% of typists tested could not reach the recommended minimum typing speed of 35 wpm, with an average speed of 27 wpm. The GAO concluded that this was due to a lack of emphasis on keyboarding skills in schools and recommended that keyboarding be included in the curriculum to improve students' typing proficiency.",
                "The 54 settlers and the 96 animals arrived here about 1902. Send 86 to us, 33 to John, 36 to Richard, and 219 to Grace. The dates were May 22, 1559; May 29, 1292; and May 8, 1426. Send 86 to us, 33 to John, 36 to Richard, and 219 to Grace. My 81 years of teaching grade 12 end June 12.",
                "It took 5 months, 4 weeks, 19 days, 16 hours, and 59 minutes. He bought 211 pounds of number 52 nails on October 31, 1923. The 69 women drove 299 miles every 31 days. The 4 men ran 16 miles 68 times in 30 events for 172 days. Mail 133 stamps and 32 letters to the 14 boys.",
                "The temperature dropped to -5°C at 3:00 AM on 12/31/2023. The recipe calls for 2½ cups of flour, 1¼ teaspoons of salt, and ¾ cup of sugar.",
                "The conference starts at 9:00 AM on 01/15/2024. Please RSVP by 12/31/2023 to confirm your attendance.",
                "The password must include at least one uppercase letter (A-Z), one lowercase letter (a-z), one number (0-9), and one special character (!@#$%^&*).",
                "The coordinates are 37.7749° N, 122.4194° W. The event is scheduled for 10:30 AM on 02/20/2024 at 123 Main St., Apt #4B.",
                "The serial number is AB-1234-CD-5678-EF. The tracking code is ZXCVBNM1234567890QWERTYUIOP.",
                "The meeting is set for 14:00 on 03/10/2024 in Room 204-B. Please bring your ID: XJ-9876-UV-5432."
            ]
            if shuffle:
                random.shuffle(base_texts)
            self.sample_text = " ".join(base_texts)

        else:  # Advanced
            # Include common special characters that are easily accessible
            advanced_texts = [
                "The 54 settlers and the 96 animals arrived here about 1902. Send 86 to us, 33 to John, 36 to Richard, and 219 to Grace. The dates were May 22, 1559; May 29, 1292; and May 8, 1426. Send 86 to us, 33 to John, 36 to Richard, and 219 to Grace. My 81 years of teaching grade 12 end June 12.",
                "In programming, variables like x = 42 and y = 'hello' are essential. Functions use () brackets!",
                "Email addresses like user@example.com contain @ symbols. Phone: (555) 123-4567.",
                "Mathematical expressions: 2 + 3 = 5, but 10 / 3 ≈ 3.33. Don't forget π ≈ 3.14159!",
                "URLs like https://www.example.com/path?query=value&other=123 use many special characters.",
                "File paths: C:\\Program Files\\App\\config.ini or /home/user/documents/file.txt work differently.",
                "JSON data: {\"name\": \"John\", \"age\": 30, \"email\": \"john@example.com\"} uses quotes and brackets.",
                "CSS selectors: .class-name, #id-name, div > p + span use special characters for styling.",
                "Regular expressions: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$ match email patterns.",
                "Command lines: ls -la /home/user | grep \"file\" > output.txt use pipes and redirection.",
                "Special characters: :;\"'<,>.?/|\\{[}]_-+=)(*&^%#@!~` are commonly used in programming.",
                "Arrays in JavaScript: var fruits = [\"apple\", \"banana\", \"cherry\"]; console.log(fruits[0]);",
                "Python dictionaries: data = {\"name\": \"John\", \"age\": 30, \"city\": \"New York\"} print(data[\"name\"])",
                "SQL queries: SELECT * FROM users WHERE name = 'John' AND age > 25 ORDER BY age DESC;",
                "HTML tags: <div class=\"container\"><p>Hello, <strong>world</strong>!</p></div> are everywhere.",
                "CSS properties: .box { width: 100px; height: 50px; background-color: #ff0000; border: 1px solid #000; }",
                "It took 5 months, 4 weeks, 19 days, 16 hours, and 59 minutes. He bought 211 pounds of number 52 nails on October 31, 1923. The 69 women drove 299 miles every 31 days. The 4 men ran 16 miles 68 times in 30 events for 172 days. Mail 133 stamps and 32 letters to the 14 boys.",
                "The temperature dropped to -5°C at 3:00 AM on 12/31/2023. The recipe calls for 2½ cups of flour, 1¼ teaspoons of salt, and ¾ cup of sugar.",
                "The conference starts at 9:00 AM on 01/15/2024. Please RSVP by 12/31/2023 to confirm your attendance.",
                "The password must include at least one uppercase letter (A-Z), one lowercase letter (a-z), one number (0-9), and one special character (!@#$%^&*).",
                "The coordinates are 37.7749° N, 122.4194° W. The event is scheduled for 10:30 AM on 02/20/2024 at 123 Main St., Apt #4B.",
                "The serial number is AB-1234-CD-5678-EF. The tracking code is ZXCVBNM1234567890QWERTYUIOP.",
                "The meeting is set for 14:00 on 03/10/2024 in Room 204-B. Please bring your ID: XJ-9876-UV-5432."
            ]
            if shuffle:
                random.shuffle(advanced_texts)
            self.sample_text = " ".join(advanced_texts)

        # Clear user input when resetting sample text
        self.user_input.set("")
        self.update_colored_text()
        return "break"  # Prevent default tab behavior

    # load_next_sample_text is no longer needed since we show all texts at once

    def reset_test(self):
        self.timer_running = False
        self.start_time = None
        self.user_input.set("")
        self.input_entry.config(state='normal')
        self.wpm = 0
        self.accuracy = 0
        self.total_words_typed = 0
        self.total_correct_chars = 0
        self.total_chars_typed = 0
        self.test_completed = False  # Reset completion flag
        # Hide stats frame
        self.stats_frame.pack_forget()
        self.timer_label.config(text="Ready to start!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTestApp(root)
    root.mainloop()