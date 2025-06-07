from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.audio import SoundLoader
from random import randint
import random

# Fixed portrait window
Window.size = (360, 640)
Window.clearcolor = (0, 0, 0, 1)
Window.minimum_width = 360
Window.minimum_height = 640
Window.maximum_width = 360
Window.maximum_height = 640
Window.resizable = False
Window.borderless = True


class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color_instruction = Color(0.2, 0.6, 1, 1)  # Store reference
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Ball(Widget):
    velocity_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # Glow effect: large, faint ellipse behind the ball
            Color(1, 0.3, 0.3, 0.25)  # Soft red glow
            self.glow = Ellipse(pos=self.pos, size=(40, 40))
            # Main ball
            Color(1, 0, 0, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        # Update glow position and size
        self.glow.pos = (self.x - 10, self.y - 10)
        self.glow.size = (self.width + 20, self.height + 20)
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size

    def move(self):
        self.y += self.velocity_y


class Particle(Widget):
    def __init__(self, pos, color, **kwargs):
        super().__init__(**kwargs)
        self.lifetime = 0.5  # seconds
        self.elapsed = 0
        self.velocity = (randint(-5, 5), randint(2, 6))
        self.color_value = color

        with self.canvas:
            self.color = Color(*self.color_value)
            self.circle = Ellipse(pos=pos, size=(5, 5))

        self.pos = pos
        Clock.schedule_interval(self.update, 1 / 60)

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.lifetime:
            if self.parent:
                self.parent.remove_widget(self)
            return False

        dx, dy = self.velocity
        self.x += dx
        self.y += dy
        self.circle.pos = self.pos
        self.color.a = 1 - (self.elapsed / self.lifetime)


class PowerUp(Widget):
    def __init__(self, kind, **kwargs):
        super().__init__(**kwargs)
        self.kind = kind  # e.g., 'slow', 'double', 'life', 'wide', 'shrink', 'reverse'
        self.size = (24, 24)
        self.velocity_y = -3
        with self.canvas:
            if kind == 'slow':
                Color(0, 1, 1, 1)
            elif kind == 'double':
                Color(1, 1, 0, 1)
            elif kind == 'life':
                Color(0, 1, 0, 1)
            elif kind == 'wide':
                Color(0.5, 0.5, 1, 1)
            elif kind == 'shrink':
                Color(1, 0.5, 0, 1)
            elif kind == 'reverse':
                Color(1, 0, 1, 1)
            else:
                Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def move(self):
        self.y += self.velocity_y


class Star(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (2, 2)
        self.speed = random.uniform(0.5, 1.5)
        x = random.randint(0, Window.width)
        y = random.randint(0, Window.height)
        with self.canvas:
            Color(1, 1, 1, random.uniform(0.3, 0.8))
            self.rect = Rectangle(pos=(x, y), size=self.size)
        self.pos = (x, y)
        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos

    def move(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = Window.height
            self.x = random.randint(0, Window.width)
        self.rect.pos = self.pos


class CatchGame(Widget):
    score = NumericProperty(0)
    misses = NumericProperty(0)
    game_over = BooleanProperty(False)
    paused = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Starfield
        self.stars = [Star() for _ in range(40)]
        for star in self.stars:
            self.add_widget(star, index=0)  # Add behind everything else

        # Load sounds
        self.catch_sound = SoundLoader.load('catch.wav')
        self.miss_sound = SoundLoader.load('miss.wav')
        self.startup_sound = SoundLoader.load('startup.wav')
        self.gameover_sound = SoundLoader.load('gameover.wav')

        self.play_startup_sound()

        # Paddle
        self.paddle = Paddle(size=(100, 20), pos=(130, 20))
        self.add_widget(self.paddle)

        # Ball
        self.ball = Ball(size=(20, 20))
        self.add_widget(self.ball)

        # Score Label
        self.score_label = Label(
            text="Score: 0",
            size_hint=(None, None),
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self.score_label.bind(texture_size=self.update_score_label_size)
        self.add_widget(self.score_label)

        # High Score
        self.high_score = self.load_high_score()
        self.high_score_label = Label(
            text=f"High Score: {self.high_score}",
            size_hint=(None, None),
            font_size=18,
            color=(1, 1, 0, 1),
        )
        self.high_score_label.bind(texture_size=self.update_high_score_label_size)
        self.add_widget(self.high_score_label)

        # Misses Bar (Health Bar)
        with self.canvas:
            self.health_bar_bg = Color(0.2, 0.2, 0.2, 1)
            self.health_bar_bg_rect = Rectangle(pos=(10, Window.height - 40), size=(90, 16))
            self.health_bar_fg = Color(1, 0, 0, 1)
            self.health_bar_fg_rect = Rectangle(pos=(10, Window.height - 40), size=(90, 16))
        # ...existing code...

        # Game Over Label
        self.over_label = Label(
            text="Game Over! Tap to Restart",
            size_hint=(None, None),
            font_size=28,
            color=(1, 0, 0, 1),
            halign='center',
            valign='middle',
            opacity=0,
        )
        self.over_label.bind(texture_size=self.update_over_label_size)
        self.add_widget(self.over_label)

        # Ready Label
        self.ready_label = Label(
            text="Ready...",
            font_size=60,
            color=(1, 1, 0, 1),
            size_hint=(None, None),
            opacity=0,
        )
        self.ready_label.bind(texture_size=self.update_ready_label_size)
        self.add_widget(self.ready_label)

        # Pause Button
        self.pause_button = Button(
            text="Pause",
            size_hint=(None, None),
            size=(80, 40),
            pos=(Window.width - 90, Window.height - 50),
            opacity=1,
        )
        self.pause_button.bind(on_release=self.toggle_pause)
        self.add_widget(self.pause_button)

        # Combo Label
        self.combo = 0
        self.multiplier = 1
        self.combo_label = Label(
            text="",
            font_size=18,
            color=(1, 1, 0, 1),
            size_hint=(None, None),
            opacity=0,
        )
        self.combo_label.bind(texture_size=self.update_combo_label_size)
        self.add_widget(self.combo_label)

        self.active_powerups = []
        self.reverse_controls = False
        self.paddle_default_width = 100
        self.paddle_wide = False
        self.paddle_shrink = False
        self.slow_motion = False
        self.double_points = False
        self.extra_life = 0
        self.powerup_timer = 0
        self.flash_timer = 0
        self.shake_offset = (0, 0)
        self.paddle_flash_timer = 0
        self.immunity = False
        self.immunity_timer = 0

        Clock.schedule_interval(self.update, 1 / 60)

    def play_startup_sound(self):
        if self.startup_sound:
            self.startup_sound.play()

    def update_score_label_size(self, instance, value):
        instance.size = instance.texture_size
        # Place score label at top left, high score to the right
        instance.pos = (10, Window.height - instance.height - 10)
        self.high_score_label.pos = (instance.right + 20, instance.y)
        # Move health bar below score label
        bar_y = instance.pos[1] - 26
        self.health_bar_bg_rect.pos = (10, bar_y)
        self.health_bar_fg_rect.pos = (10, bar_y)

    def update_high_score_label_size(self, instance, value):
        instance.size = instance.texture_size

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def update_health_bar(self):
        # 3 max health, decrease width as misses increase
        max_width = 90
        health = max(0, 3 - self.misses)
        width = max_width * (health / 3)
        self.health_bar_fg_rect.size = (width, 16)

    def start_ready(self):
        self.ready_label.opacity = 1
        self.paused = True
        Clock.schedule_once(self.start_game, 2)

    def start_game(self, dt):
        self.ready_label.opacity = 0
        self.paused = False
        self.reset_ball()

    def reset_ball(self):
        self.ball.center_x = randint(20, Window.width - 20)
        self.ball.top = Window.height
        # Custom speed curve: slow increase until 250, then only increase at 400, 800, etc.
        base_speed = -4
        if self.score < 250:
            speed = base_speed - self.score * 0.05
        elif self.score < 400:
            speed = base_speed - 250 * 0.05 - ((self.score - 250) // 150) * 0.5
        elif self.score < 800:
            speed = base_speed - 250 * 0.05 - 1 * 0.5 - ((self.score - 400) // 400) * 0.5
        else:
            speed = base_speed - 250 * 0.05 - 1 * 0.5 - 1 * 0.5 - ((self.score - 800) // 800) * 0.5
        self.ball.velocity_y = speed

    def spawn_particles(self, pos, color, count=5):
        for _ in range(count):
            particle = Particle(pos=pos, color=color)
            self.add_widget(particle)

    def update_combo_label_size(self, instance, value):
        instance.size = instance.texture_size
        instance.pos = (Window.width / 2 - instance.width / 2, Window.height - 60)

    def spawn_powerup(self):
        # 1/10 chance per catch
        if random.random() < 0.1:
            kind = random.choice(['slow', 'double', 'life', 'wide', 'shrink'])  # removed 'reverse'
            powerup = PowerUp(kind=kind, pos=(random.randint(20, Window.width - 44), Window.height - 40))
            self.add_widget(powerup)
            self.active_powerups.append(powerup)

    def update(self, dt):
        Window.clearcolor = (0, 0, 0, 1)
        for star in self.stars:
            star.move()
        # Paddle flash effect after miss
        if self.paddle_flash_timer > 0:
            self.paddle_flash_timer -= dt
            # Set paddle color to white by updating the Color instruction
            self.paddle.color_instruction.rgb = (1, 1, 1)
        else:
            self.paddle.color_instruction.rgb = (0.2, 0.6, 1)
        # Immunity timer
        if self.immunity:
            self.immunity_timer -= dt
            if self.immunity_timer <= 0:
                self.immunity = False
        if self.game_over or self.paused:
            return

        # PowerUp movement
        for powerup in self.active_powerups[:]:
            powerup.move()
            if powerup.y < 0:
                self.remove_widget(powerup)
                self.active_powerups.remove(powerup)
            elif (powerup.y <= self.paddle.top + 10 and abs(powerup.center_x - self.paddle.center_x) < self.paddle.width / 2):
                self.apply_powerup(powerup.kind)
                self.spawn_particles(pos=powerup.pos, color=(1, 1, 1, 1), count=15)
                self.remove_widget(powerup)
                self.active_powerups.remove(powerup)

        # Ball move (slow motion)
        if self.slow_motion:
            self.ball.y += self.ball.velocity_y * 0.5
        else:
            self.ball.move()

        # Combo/multiplier logic
        if (self.ball.y <= self.paddle.top and abs(self.ball.center_x - self.paddle.center_x) < self.paddle.width / 2 and self.ball.velocity_y < 0):
            self.combo += 1
            if self.combo > 1:
                self.multiplier = min(5, 1 + self.combo // 5)
                self.combo_label.text = f"Combo x{self.combo}! Multiplier: {self.multiplier}x"
                self.combo_label.opacity = 1
            else:
                self.multiplier = 1
                self.combo_label.opacity = 0
            self.score += 1 * self.multiplier * (2 if self.double_points else 1)
            if self.catch_sound:
                self.catch_sound.play()
            self.spawn_particles(pos=self.ball.pos, color=(0, 1, 0, 1), count=8)
            self.reset_ball()
            self.spawn_powerup()
        elif self.ball.y < 0:
            if not self.immunity:
                self.combo = 0
                self.multiplier = 1
                self.combo_label.opacity = 0
                self.misses += 1
                if self.miss_sound:
                    self.miss_sound.play()
                self.spawn_particles(pos=self.ball.pos, color=(1, 0, 0, 1), count=5)
                self.paddle_flash_timer = 0.4
                self.immunity = True
                self.immunity_timer = 1.0
                if self.misses >= 3:
                    self.trigger_game_over()
                else:
                    self.reset_ball()
            else:
                self.reset_ball()
        self.score_label.text = f"Score: {self.score}"
        self.update_health_bar()

    def trigger_game_over(self):
        self.game_over = True
        self.over_label.opacity = 1
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.high_score_label.text = f"High Score: {self.high_score}"
        if self.gameover_sound:
            self.gameover_sound.play()

    def restart(self):
        self.score = 0
        self.misses = 0
        self.game_over = False
        self.over_label.opacity = 0
        self.play_startup_sound()
        self.start_ready()

    def toggle_pause(self, *args):
        self.paused = not self.paused
        self.pause_button.text = "Resume" if self.paused else "Pause"

    def apply_powerup(self, kind):
        if kind == 'slow':
            self.slow_motion = True
            Clock.schedule_once(lambda dt: setattr(self, 'slow_motion', False), 7)
        elif kind == 'double':
            self.double_points = True
            Clock.schedule_once(lambda dt: setattr(self, 'double_points', False), 7)
        elif kind == 'life':
            if self.misses > 0:
                self.misses -= 1
                self.update_health_bar()
        elif kind == 'wide':
            self.paddle.width = self.paddle_default_width * 2
            Clock.schedule_once(lambda dt: setattr(self.paddle, 'width', self.paddle_default_width), 8)
        elif kind == 'shrink':
            self.paddle.width = self.paddle_default_width * 0.4
            Clock.schedule_once(lambda dt: setattr(self.paddle, 'width', self.paddle_default_width), 8)

    def on_touch_move(self, touch):
        if touch.y > 100 and not self.game_over and not self.paused:
            # Remove reverse controls logic
            self.paddle.center_x = touch.x
            if self.paddle.x < 0:
                self.paddle.x = 0
            if self.paddle.right > Window.width:
                self.paddle.right = Window.width

    def on_touch_down(self, touch):
        if self.game_over:
            self.restart()

    def update_over_label_size(self, instance, value):
        instance.size = instance.texture_size
        instance.pos = ((Window.width - instance.width) / 2, (Window.height - instance.height) / 2)

    def update_ready_label_size(self, instance, value):
        instance.size = instance.texture_size
        instance.pos = ((Window.width - instance.width) / 2, (Window.height - instance.height) / 2)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        self.high_score = self.load_high_score()
        title = Label(text="Catch Game", font_size=48, size_hint=(1, 0.4), color=(1, 1, 1, 1))
        subtitle = Label(text="Made by Gwen", font_size=24, size_hint=(1, 0.2), color=(1, 1, 1, 1))
        high_score_label = Label(text=f"High Score: {self.high_score}", font_size=22, size_hint=(1, 0.2), color=(1, 1, 0, 1))
        play_button = Button(text="PLAY", size_hint=(1, 0.2), font_size=24)
        quit_button = Button(text="QUIT", size_hint=(1, 0.2), font_size=24)
        play_button.bind(on_release=self.play_game)
        quit_button.bind(on_release=self.quit_game)
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(high_score_label)
        layout.add_widget(play_button)
        layout.add_widget(quit_button)
        self.add_widget(layout)

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def play_game(self, *args):
        self.manager.current = 'game'

    def quit_game(self, *args):
        App.get_running_app().stop()


class CatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = CatchGame()
        self.game.paused = True
        self.add_widget(self.game)

    def on_enter(self):
        self.game.restart()
        self.game.paused = False


class CatchApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(CatchScreen(name='game'))
        return sm


if __name__ == '__main__':
    CatchApp().run()
