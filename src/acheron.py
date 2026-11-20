import argparse
import math
import os
import platform
import select
import shutil
import sys
import time
from contextlib import contextmanager

try:
    import psutil
except ImportError:
    psutil = None

RESET = "\x1b[0m"
MINT = "\x1b[38;5;115m"
SEA = "\x1b[38;5;81m"
LILAC = "\x1b[38;5;183m"
DIM = "\x1b[38;5;245m"
WARM = "\x1b[38;5;222m"


def color(value, tone, enabled):
    return f"{tone}{value}{RESET}" if enabled else value


def bar(value, size=18):
    filled = round(max(0.0, min(100.0, value)) * size / 100)
    return "[" + "#" * filled + "." * (size - filled) + "]"


def rate(value):
    units = ("B/s", "KB/s", "MB/s", "GB/s")
    amount = float(value)
    for unit in units:
        if amount < 1000 or unit == units[-1]:
            return f"{amount:.0f} {unit}" if unit == units[0] else f"{amount:.1f} {unit}"
        amount /= 1000


def mood(cpu, memory, traffic):
    if memory >= 90:
        return "The roots are carrying a lot. A little breathing room may help."
    if cpu >= 85:
        return "A bright burst of activity. The whole canopy is awake."
    if traffic >= 1_000_000:
        return "Signals are crossing the valley in a steady stream."
    if cpu < 12 and memory < 65:
        return "A quiet patch of cosmos. Take a breath; everything can wait."
    return "The ecosystem is in balance, growing at its own pace."


def landscape(width, cpu, memory, beat):
    width = max(24, width)
    sky = [" "] * width
    for n in range(max(5, width // 11)):
        x = (n * 37 + beat * (1 + n % 3) * 2) % width
        sky[x] = "." if n % 3 else "*"
    distant = [" "] * width
    near = [" "] * width
    ground = [" "] * width
    for x in range(width):
        phase = x * 0.17 + beat * 0.12
        far_peak = int(2 + math.sin(phase) * 1.4)
        near_peak = int(3 + math.sin(phase * 0.72 + 1.7) * (1.3 + cpu / 70))
        if far_peak == 0:
            distant[x] = "/"
        elif far_peak == 1:
            distant[x] = "^"
        elif far_peak == 2:
            distant[x] = "\\"
        if near_peak <= 2:
            near[x] = "^" if near_peak == 2 else "/"
        elif near_peak == 3:
            near[x] = "\\"
        if x % 7 == beat % 7:
            ground[x] = "o" if memory < 80 else "+"
        elif x % 11 == (beat * 2) % 11:
            ground[x] = "~"
    return "".join(sky), "".join(distant), "".join(near), "".join(ground)


def terminal_lines(cpu, memory, received, sent, beat, width, enabled):
    inner = max(38, width - 4)

    def line(text="", tone=DIM):
        return "  " + color(text[:inner].ljust(inner), tone, enabled)

    cpu_text = f"CPU     {cpu:5.1f}%  {bar(cpu, 16)}"
    mem_text = f"MEMORY  {memory:5.1f}%  {bar(memory, 16)}"
    net_text = f"IN   {rate(received):>10}     OUT   {rate(sent):>10}"
    stars, ridge, canopy, soil = landscape(inner, cpu, memory, beat)
    return [
        line("ACHERON   /   A LIVING LOOK AT MACHINE WEATHER", MINT),
        line("-" * inner),
        line("  A small world, growing with your system", LILAC),
        line(),
        line(stars, DIM),
        line(ridge, SEA),
        line(canopy, MINT),
        line(soil, WARM),
        line(),
        line(cpu_text, SEA),
        line(mem_text, MINT),
        line(net_text, LILAC),
        line(),
        line(mood(cpu, memory, received + sent), WARM),
        line("Q  leave gently     Ctrl+C  also returns you home", DIM),
    ]


def render(cpu, memory, received, sent, beat=0, stream=None):
    stream = stream or sys.stdout
    enabled = stream.isatty() and "NO_COLOR" not in os.environ
    width = shutil.get_terminal_size((80, 24)).columns
    lines = terminal_lines(cpu, memory, received, sent, beat, width, enabled)
    if stream.isatty():
        stream.write("\x1b[H\x1b[2J")
    stream.write("\n".join(lines) + "\n")
    stream.flush()


@contextmanager
def keyboard_mode():
    if not sys.stdin.isatty():
        yield
        return
    if platform.system() == "Windows":
        yield
        return
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    previous = termios.tcgetattr(descriptor)
    try:
        tty.setcbreak(descriptor)
        yield
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, previous)


def pressed_key():
    if not sys.stdin.isatty():
        return ""
    if platform.system() == "Windows":
        import msvcrt

        if msvcrt.kbhit():
            return msvcrt.getwch().lower()
        return ""
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.read(1).lower() if ready else ""


def snapshot():
    psutil.cpu_percent(interval=None)
    network = psutil.net_io_counters()
    time.sleep(0.12)
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    current = psutil.net_io_counters()
    received = max(0, current.bytes_recv - network.bytes_recv) / 0.12
    sent = max(0, current.bytes_sent - network.bytes_sent) / 0.12
    return cpu, memory, received, sent, current


def run(once=False):
    if psutil is None:
        raise RuntimeError("Acheron needs psutil. Re-run the installer to add it.")
    cpu, memory, received, sent, previous = snapshot()
    if once or not sys.stdout.isatty():
        render(cpu, memory, received, sent, 0)
        return
    columns = shutil.get_terminal_size((80, 24)).columns
    sys.stdout.write("\x1b[?1049h\x1b[?25l")
    sys.stdout.flush()
    started = time.monotonic()
    try:
        with keyboard_mode():
            while True:
                now = time.monotonic()
                elapsed = max(0.01, now - started)
                started = now
                cpu = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory().percent
                current = psutil.net_io_counters()
                received = max(0, current.bytes_recv - previous.bytes_recv) / elapsed
                sent = max(0, current.bytes_sent - previous.bytes_sent) / elapsed
                previous = current
                columns = shutil.get_terminal_size((80, 24)).columns
                render(cpu, memory, received, sent, int(now * 3), sys.stdout)
                if pressed_key() == "q":
                    break
                time.sleep(0.45)
    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(prog="acheron", description="A small, living view of your system.")
    parser.add_argument("--once", action="store_true", help="show one snapshot and exit")
    arguments = parser.parse_args()
    try:
        run(arguments.once)
    except KeyboardInterrupt:
        if sys.stdout.isatty():
            sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
            sys.stdout.flush()
    except RuntimeError as error:
        print(f"acheron: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
