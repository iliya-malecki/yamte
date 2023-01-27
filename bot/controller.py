#!/usr/bin/env python
#%%
from pynput import mouse, keyboard
import json
import pandas as pd
import time
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
#%%
def make_mimic(data: pd.DataFrame):
    data = data.copy()
    loop_start = (data['repeat'] == 'below').idxmax()
    loop_end = (data['repeat'] == 'above').idxmax()

    repeats = 20
    if loop_start > 0 and loop_end > 0:
        data = pd.concat(
            [data.loc[:loop_start-1]]
            + [data.loc[loop_start+1:loop_end-1]] * repeats
            + [data.loc[loop_end+1:]],
            ignore_index=True
        )

    return data



def make_justpoints(data):
    data = make_mimic(data)
    return (
        pd.concat([
            data
                .query('reason!="scroll"')
                .groupby((data['mousedown'] != data['mousedown'].shift(1)).cumsum())
                .head(1),
            data.query('reason=="scroll"')
        ])
        .sort_index()
    )


def make_splines(data, kind='linear'):
    df = make_justpoints(data)

    df['dist'] = (
        df[['x','y']]
        .diff()
        .pow(2).sum(axis=1).pow(0.5)
        .clip(lower=0.01)
        .cumsum()
    )

    interpolator = pd.concat([
        pd.Series(np.arange(df['dist'].min(), df['dist'].max(), 6.5), name='dist')
            .to_frame()
            .assign(mousedown=False, reason='move'),
        df.query('reason=="click"')[['dist','mousedown','reason']]
    ]).sort_values('dist')

    interpolator[['x','y']] = (
        df.query('reason!="scroll"').pipe(
            lambda df:
            interp1d(df['dist'], df[['x','y']].T, kind=kind)(interpolator['dist']).T
        )
    )
    interpolator['t'] = pd.Timedelta(seconds=0.005)


    res = (
        pd.concat([
            interpolator,
            df.query('reason=="scroll"').drop(columns=['x','y'])
        ])
        .sort_values('dist')
    )
    scroll_end = (res['reason'].shift(-1)=='scroll') & (res['reason']!='scroll' )
    res.loc[scroll_end, 'y'] = res.loc[scroll_end, 'y'].clip(lower=135)
    return res


def kbpress(queue):
    # a very crude and cruel queue for killing the main thread
    def _f(key):
        if key == keyboard.Key.esc:
            queue.append(1)
    return _f


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('requested_method', default='cubic', nargs='?')
    parser.add_argument('--file_index', default=None)
    return parser.parse_args()
#%%
# do i need to sometimes do a click instead of press, release?
def main():

    args = parse_args()
    path = Path('./movement_data').absolute()
    if args.file_index is not None:
        filename = path/f'history_{args.file_index}.json'
    else:
        filename = sorted(path.glob('history_*.json'))[-1]
    with open(filename) as f:
        data = pd.json_normalize(json.load(f))
        data['mousedown'] = data['mousedown'].fillna(False).astype(bool)
        data['t'] = pd.to_datetime(data['t']).diff().shift(-1)


    match args.requested_method:
        case 'mimic':
            data = make_mimic(data)
        case 'points':
            data = make_justpoints(data)
        case 'lines':
            data = make_splines(data)
        case 'splines':
            data = make_splines(data, 'cubic')
        case interpolation_method:
            print(f'{interpolation_method = }')
            data = make_splines(data, interpolation_method)

    time.sleep(2)

    gottadie = []
    mc = mouse.Controller()
    with keyboard.Listener(on_press=kbpress(gottadie)) as kb:
        pressed = False
        for idx, row in data.iterrows():
            if gottadie:
                break
            if row[['x','y']].notna().all():
                mc.position = (row['x'], row['y'])
            if row['mousedown'] and not pressed:
                time.sleep(0.2)
                mc.press(mouse.Button.left)
                pressed = True
            if pressed and not row['mousedown']:
                time.sleep(0.15)
                mc.release(mouse.Button.left)
                pressed = False
            if row['reason'] == 'scroll':
                mc.scroll(row['dx'], row['dy'])
            if row['t'].total_seconds() > 0:
                time.sleep(row['t'].total_seconds())


#%%
if __name__ == '__main__':
    main()

# %%
