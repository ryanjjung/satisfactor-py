# Satisfactor-Py

A Python utility for planning factories in the video game [Satisfactory](https://www.satisfactorygame.com/). Much information here is taken from the [Satisfactory Wiki](https://satisfactory.wiki.gg/wiki/Satisfactory_Wiki).


## Setup

The `satisfactory` library has no dependencies and may be used as described in this Readme.

Some other scripts depend on third party libraries. Install them with:

```
pip install -r requirements.txt
```

`factory_designer_gtk` (the factory designer) requires GTK 4.13 or later. Install it and the Python bindings for GObject. On Fedora 40, you run:

```
dnf install gtk4 python3-gobject
```


## Run Something

If you want to run the GTK Factory Designer, see the [section below](#factory-designer-gtk-application).

If you're interested in the underlying library, a good place to start is the [screw factory test script](./scripts/screw_factory.py):

```
PYTHONPATH=. ./scripts/screw_factory.py
```

This product has never been tested on Windows, though you may be able to [find help here](https://www.gtk.org/docs/installations/windows), or [here for Macs](https://www.gtk.org/docs/installations/macos/).


### Factory Designer GTK Application

This is a point-and-click GTK-based graphical desktop application allowing for easy factory design.

It uses images which are copyrighted, and which I don't like the idea of storing in a git repo. In order to use these in the application, you'll need to run this command with an internet connection:

```
PYTHONPATH=. ./scripts/collect_images.py
```

To run the UI:

```
PYTHONPATH=. ./gtk_factory_designer.py
```