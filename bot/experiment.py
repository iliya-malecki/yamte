#!/usr/bin/env python
#%%
from pynput import mouse
import time

def main():

    with mouse.Controller() as mc:
        for n in range(20):
            time.sleep(1)
            mc.press(mouse.Button.left)
            time.sleep(1)
            mc.release(mouse.Button.left)


#%%
if __name__ == '__main__':
    main()

# %%
