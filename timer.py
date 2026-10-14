import os
import json
import time
import threading
import subprocess
import urllib.parse

# =========================
# CONFIG
# =========================

BOTS = [(b["url"], os.environ.get(b["token_env"])) for b in json.loads(os.getenv("TS_BOTS", "[]"))]

ACTIVE = os.getenv("AUDIO_ACTIVE", "/app/audio/active.opus")
WARN40 = os.getenv("AUDIO_WARN40", "/app/audio/warning-40.opus")
WARN20 = os.getenv("AUDIO_WARN20", "/app/audio/warning-20.opus")
ZEAL = os.getenv("AUDIO_ZEAL", "/app/audio/zeal.opus")
SPAM = os.getenv("AUDIO_SPAM", "/app/audio/shield.opus")

VOLUME = 100

timer_thread = None
stop_event = threading.Event()


# =========================
# TS3 AUDIOBOT API
# =========================

def api_command(command, argument=None):
    def send_to_bot(api_base, token):
        if not token:
            print(f"[ERROR] Missing token for {api_base}")
            return False

        url = api_base + "/" + command

        if argument is not None:
            encoded_argument = urllib.parse.quote(str(argument), safe="")
            url += "/" + encoded_argument

        try:
            result = subprocess.run(
                [
                    "curl",
                    "-sS",
                    "-u",
                    token,
                    url
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"[CURL ERROR] {api_base} -> {result.stderr.strip()}")
                return False

            if result.stdout.strip():
                print(f"[API] {api_base} -> {result.stdout.strip()}")

            return True

        except Exception as e:
            print(f"[API ERROR] {api_base} -> {e}")
            return False

    threads = []

    for api_base, token in BOTS:
        t = threading.Thread(
            target=send_to_bot,
            args=(api_base, token)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return True

def play(sound):
    print(f"[PLAY] {sound}")
    api_command("play", sound)


def stop_audio():
    api_command("stop")


def set_volume():
    api_command("volume", VOLUME)


# =========================
# TIMER
# =========================

def wait_until(start_time, target_seconds):
    while not stop_event.is_set():

        elapsed = time.monotonic() - start_time
        remaining = target_seconds - elapsed

        if remaining <= 0:
            return True

        stop_event.wait(min(remaining, 0.25))

    return False


def run_timer():
    start_time = time.monotonic()

    print()
    print("=========================")
    print("=== TeamSpeak TIMER STARTED ===")
    print("=========================")

    # Volume 100
    set_volume()

    # Immediate start sound
    play(ACTIVE)

    events = []

    # -------------------------
    # ZEAL
    # Every 3 minutes
    # 03:00 / 06:00 / 09:00...
    # -------------------------

    for zeal_time in range(180, 1501, 180):
        events.append(
            (zeal_time, ZEAL, "ZEAL")
        )

    # -------------------------
    # SPAM SHIELD NAMELESS
    # Every 65 seconds
    # 01:05 / 02:10 / 03:15...
    # -------------------------

    for spam_time in range(65, 1501, 65):

        # Disable SPAM from Jungle -40s until Jungle +15s.
        # Jungle times: 05:00 / 10:00 / 15:00 / 20:00 / 25:00
        in_jungle_window = any(
            jungle_time - 40 <= spam_time <= jungle_time + 15
            for jungle_time in range(300, 1501, 300)
        )

        if in_jungle_window:
            print(
                f"[SPAM SKIP] "
                f"{spam_time // 60:02d}:{spam_time % 60:02d} "
                f"(Jungle protection)"
            )
            continue

        events.append(
            (spam_time, SPAM, "SPAM SHIELD NAMELESS")
        )

    # -------------------------
    # JUNGLE
    # Every 5 minutes
    #
    # Jungle:
    # 05:00
    # 10:00
    # 15:00
    # 20:00
    # 25:00
    #
    # Warnings:
    # 40 sec
    # 20 sec
    # -------------------------

    for jungle_time in range(300, 1501, 300):

        events.append(
            (
                jungle_time - 40,
                WARN40,
                "JUNGLE - 40 SEC"
            )
        )

        events.append(
            (
                jungle_time - 20,
                WARN20,
                "JUNGLE - 20 SEC"
            )
        )


    # Sort all events by time
    events.sort(key=lambda event: event[0])

    # Run events
    for event_time, sound, name in events:

        if stop_event.is_set():
            break

        if not wait_until(start_time, event_time):
            break

        if stop_event.is_set():
            break

        minutes = event_time // 60
        seconds = event_time % 60

        print()
        print(
            f"[{minutes:02d}:{seconds:02d}] {name}"
        )

        play(sound)

    if stop_event.is_set():
        print()
        print("=== TeamSpeak TIMER STOPPED ===")

    else:
        print()
        print("=== TeamSpeak TIMER FINISHED ===")


# =========================
# COMMANDS
# =========================

def start_timer():
    global timer_thread

    if timer_thread is not None:
        if timer_thread.is_alive():
            print("Timer already running.")
            return

    stop_event.clear()

    timer_thread = threading.Thread(
        target=run_timer,
        daemon=True
    )

    timer_thread.start()


def stop_timer():
    stop_event.set()

    stop_audio()

    print("Timer stopped.")


def timer_status():
    if (
        timer_thread is not None
        and timer_thread.is_alive()
        and not stop_event.is_set()
    ):
        print("Timer: RUNNING")

    else:
        print("Timer: STOPPED")


# =========================
# START PROGRAM
# =========================

missing_tokens = []

for i, (_, token) in enumerate(BOTS, start=1):
    if not token:
        missing_tokens.append(str(i))

if missing_tokens:
    print()
    print("WARNING: Missing TS3 tokens for bots: " + ", ".join(missing_tokens))
    print("Run:")
    print("Configure the token variables referenced by TS_BOTS.")
    print()

print()
print("TeamSpeak Announcement Timer")
print()
print("start   = Start timer")
print("stop    = Stop timer")
print("status  = Timer status")
print("quit    = Exit")
print()

FIFO_PATH = "/run/teamspeak-ts-timer/control"

if not os.path.exists(FIFO_PATH):
    os.mkfifo(FIFO_PATH)

print(f"Control pipe: {FIFO_PATH}")

while True:
    try:
        with open(FIFO_PATH, "r") as fifo:
            for line in fifo:
                command = line.strip().lower()

                if command == "start":
                    start_timer()

                elif command == "stop":
                    stop_timer()

                elif command == "status":
                    timer_status()

                elif command in ("quit", "exit"):
                    stop_timer()
                    raise SystemExit

    except KeyboardInterrupt:
        print()
        stop_timer()
        break
