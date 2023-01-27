from pynput import mouse, keyboard
from datetime import datetime
import json
import time
import re
from pathlib import Path

time.sleep(1)
print('recording started, press esc to stop and save to history.json')
print('to start a loop, press `arrow down` key, to stop it - press `arrow up`')

state = {
    'history': [],
    'mousedown': False,
}
path = Path('./movement_data')
path.mkdir(exist_ok=True)
path = path.absolute()

def update_history(x, y, dx, dy, reason):
    state['history'].append({
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy,
        't': datetime.now(),
        'mousedown': state['mousedown'],
        'reason': reason,
    })


def on_click(x, y, button, pressed):
    state['mousedown'] = pressed
    update_history(x, y, None, None, 'click')


def make_kbpress(mouse_listener, path):
    def kbpress(key):
        if key == keyboard.Key.esc:
            mouse_listener.stop()

            numbers = [
                int(re.search("history_(\d+).json", s.name).group(1))
                for s in path.glob('history_*.json')
            ] or [0]

            print('esc pressed, saving data to history.json')
            with open(path/f"history_{max(numbers)+1}.json", 'w') as f:
                json.dump(state['history'], f, default=str)
            quit()
        elif key == keyboard.Key.down:
            print('down arrow pressed, insering a `repeat:below` delimiter into the history')
            state['history'].append({
                'repeat':'below'
            })
        elif key == keyboard.Key.up:
            print('up arrow pressed, insering a `repeat:above` delimiter into the history')
            state['history'].append({
                'repeat':'above'
            })

    return kbpress


mouse_listener = mouse.Listener(
    on_move=lambda x,y: update_history(x, y, None, None, reason='move'),
    on_click=on_click,
    on_scroll=lambda x, y, dx, dy: update_history(x, y, dx, dy, reason='scroll')
)
mouse_listener.start()

with keyboard.Listener(
    on_release=make_kbpress(mouse_listener, path)
) as kb:
    kb.join()
