This is a script designed to be triggered by Keyboard Maestro to control the position and size of
the frontmost window.

To set up KM, import the `kmmacros` file and customise the hotkeys if you wish. The name of the
macro is passed to the script in order to determine the operation.

To run manually, run `./resize.py [keyname]` where `[keyname]` is the name of the key that was
used in the KM hotkey. For example:

```bash
./resize left
./resize up
./resize enter
./resize rightwards
```

# TODO

- [x] If the window is half-screen-size and the orthogonal key is pressed, make it quarter-size
- [x] +Shift key to shift up/down/l/r but retain size
- [ ] Move onto other desktops if at the edge of the screen and there is another desktop in that
      direction
- [ ] If the desktop is portrait, lateral movements are full width
