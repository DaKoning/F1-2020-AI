import pyglet
import time

from pyglet import window

win = pyglet.window.Window(629, 1010, caption='F1-2020-AI - Monza (Italy)')
win.set_location(1920, 30)
icon = pyglet.image.load('Assets/F1.png')
win.set_icon(icon)

batch = pyglet.graphics.Batch()

tracklayout = pyglet.sprite.Sprite(pyglet.image.load('Tracklayout.png'))
playericon = pyglet.image.load('Assets/Playericon7.png')


@win.event
def on_draw():
    win.clear()
    tracklayout.draw()
    player.draw()
    batch.draw()

player_pos = 500, 500
player = pyglet.sprite.Sprite(playericon, player_pos[0], player_pos[1])
player.rotation = 60

line1 = pyglet.shapes.Line(500, 500, 600, 600, 2, color=(255, 255, 0), batch=batch)


time.sleep(3)

line1 = pyglet.shapes.Line(500, 500, 700, 700, 2, color=(255, 0, 0), batch=batch)