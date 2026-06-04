import tkinter as tk
from datetime import datetime
from datetime import timedelta
import simpleaudio as sa
import threading

def play_alarm_sound(sound_file):
    """Function to play sound in a separate thread."""
    try:
        # Load the .wav file
        wave_obj = sa.WaveObject.from_wave_file(r'"C:\Users\LENOVO\Music\Salama.mp3"')
        # Play the sound. This call is non-blocking.
        play_obj = wave_obj.play()
        # play_obj.wait_done()  # Uncomment this line if you want the program to wait for the sound to finish.
    except Exception as e:
        print(f"Error playing sound: {e}")

def show_timer_window(stop_time):
    """Create a sports-watch style countdown window."""
    root = tk.Tk()
    root.title("Countdown Timer")
    root.geometry("500x200")
    root.configure(bg="black")
    root.resizable(False, False)

    # Center window
    root.eval('tk::PlaceWindow . center')

    # Glow label (behind, slightly larger and darker)
    glow_label = tk.Label(
        root,
        text="00:00:00",
        font=("Consolas", 68, "bold"),
        fg="#006600",        # dark green glow
        bg="black"
    )
    glow_label.place(relx=0.5, rely=0.5, anchor="center")

    # Main label (foreground, bright neon green)
    main_label = tk.Label(
        root,
        text="00:00:00",
        font=("Consolas", 64, "bold"),
        fg="#00FF00",        # bright neon green
        bg="black"
    )
    main_label.place(relx=0.5, rely=0.5, anchor="center")

    def update():
        now = datetime.now()
        remaining = stop_time - now
        total_secs = int(remaining.total_seconds())

        if total_secs <= 0:
            main_label.config(text="00:00:00", fg="red")
            glow_label.config(text="00:00:00", fg="#330000")  # dark red glow
            # --- Trigger the sound alert in a separate thread ---
            # Replace 'alarm_sound.wav' with the path to your sound file
            sound_thread = threading.Thread(target=play_alarm_sound, args=("alarm_sound.wav",))
            sound_thread.daemon = True
            sound_thread.start()
            # ----------------------------------------------------
            root.after(2000, root.destroy)
            return

        hours = total_secs // 3600
        minutes = (total_secs % 3600) // 60
        seconds = total_secs % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        main_label.config(text=time_str)
        glow_label.config(text=time_str)

        root.after(1000, update)

    update()
    root.mainloop()

# ----- Terminal input -----
if __name__ == "__main__":
    input_time = input("Enter stop time (HH:MM, 24h): ")
    now = datetime.now()
    stop_time = datetime.strptime(input_time, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    if stop_time < now:
        stop_time += timedelta(days=1)

    show_timer_window(stop_time)
    print("Timer window opened. Close it to exit.")
