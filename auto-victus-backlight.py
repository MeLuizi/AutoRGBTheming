import glob
import re
import subprocess
from pathlib import Path

# Configuration paths and device patterns
CONFIG_FILE = Path("/home/harrys/.config/hypr/scheme/current.lua")
KEYBOARD_PATTERN = '/sys/class/leds/hp*kbd*/multi_intensity'

def extract_primary_hex(file_path: Path) -> str:
    """Reads the theme file and extracts the 6-digit primary hex code."""
    content = file_path.read_text(encoding='utf-8')
    match = re.search(r'\bprimary\s*=\s*"([0-9a-fA-F]{6})"', content)
    
    if not match:
        raise ValueError(f"Could not find 'primary' color in {file_path}")
        
    return match.group(1)

def enhance_color_vibrancy(r: int, g: int, b: int):
    """Adjusts color balance and scales up brightness so LEDs pop vividly."""
    # Suppress the weakest channel to prevent warm or cool tones from washing out
    if r > b and g > b:
        b = int(b * 0.1)
    elif g > r and b > r:
        r = int(r * 0.1)
    elif r > g and b > g:
        g = int(g * 0.1)
    
    # Scale up to max brightness (255)
    max_val = max(r, g, b)
    if 0 < max_val < 255:
        scale = 255.0 / max_val
        r = min(255, int(r * scale))
        g = min(255, int(g * scale))
        b = min(255, int(b * scale))
        
    return r, g, b

def update_keyboard(r: int, g: int, b: int):
    """Sends the RGB values to all detected HP keyboard backlights."""
    rgb_text = f"{r} {g} {b}"
    
    for path in glob.glob(KEYBOARD_PATTERN):
        try:
            subprocess.run(
                ['sudo', 'tee', path],
                input=rgb_text.encode('utf-8'),
                check=True,
                stdout=subprocess.DEVNULL
            )
            print(f"Updated keyboard LED: {path}")
        except subprocess.SubprocessError as error:
            print(f"Failed to update keyboard at {path}: {error}")

def update_mouse(r: int, g: int, b: int):
    """Sends the adjusted color to OpenRGB for the mouse peripheral."""
    try:
        hex_color = f"{r:02X}{g:02X}{b:02X}"
        subprocess.run(
            ['openrgb', '--device', '0', '--mode', 'static', '--color', hex_color],
            check=True
        )
        print(f"Updated mouse color to #{hex_color}")
    except subprocess.SubprocessError as error:
        print(f"Failed to update mouse: {error}")

def main():
    # 1. Read the theme file to get the base color
    hex_code = extract_primary_hex(CONFIG_FILE)
    
    # 2. Convert hex into RGB integer values
    r, g, b = bytes.fromhex(hex_code)
    
    # 3. Apply hardware vibrancy and brightness boosts
    r, g, b = enhance_color_vibrancy(r, g, b)
    
    # 4. Push the final colors to your hardware devices
    update_keyboard(r, g, b)
    update_mouse(r, g, b)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")