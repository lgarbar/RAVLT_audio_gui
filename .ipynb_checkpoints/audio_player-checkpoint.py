import pygame
import time

def play_music_segment(file_path, start_ms, end_ms):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        print(f"Playing segment from {start_ms} ms to {end_ms} ms")

        # Start playback
        pygame.mixer.music.play()

        # Wait for a short time to allow playback to start
        time.sleep(0.1)

        # Set the starting position
        pygame.mixer.music.set_pos(start_ms / 1000.0)

        # Wait for the specified duration
        while pygame.mixer.music.get_pos() < end_ms - start_ms:
            time.sleep(0.01)
        print('uwu')

    except pygame.error as e:
        print(f"Error: {e}")

    finally:
        pygame.mixer.quit()
        pygame.quit()

if __name__ == "__main__":
    mp3_file_path = "/data2/Projects/NKI_RS2/RAVLT/ravlt_audio_gui/test_audio.mp3"  # Replace with the path to your MP3 file
    start_time = 4600  # Start time in milliseconds
    end_time = 6000    # End time in milliseconds

    play_music_segment(mp3_file_path, start_time, end_time)
