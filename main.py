from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from random import randint, choice

# Magos do Infinito — prototype 1.0
# Designed for touch screens and low-powered Android devices.

Window.clearcolor = (0.025, 0.035, 0.09, 1)

BG = (0.025, 0.035, 0.09, 1)
PANEL = (0.055, 0.085, 0.17, 1)
BLUE = (0.12, 0.55, 1, 1)
CYAN = (0.2, 0.9, 1, 1)
GOLD = (1, 0.76, 0.24, 1)
RED = (1, 0.22, 0.32, 1)
GREEN = (0.25, 0.9, 0.55, 1)
WHITE = (0.9, 0.94, 1, 1)
MUTED = (0.57, 0.68, 0.82, 1)

class PixelButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0.08, 0.19, 0.36, 1))
        kwargs.setdefault("color", WHITE)
        kwargs.setdefault("font_size", "15sp")
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)

class Panel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*PANEL)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
    def _update_rect(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RPGApp(App):
    def build(self):
        self.title = "Magos do Infinito"
        self.player_max_hp = 100
        self.player_hp = 100
        self.player_max_mp = 60
        self.player_mp = 60
        self.level = 1
        self.exp = 0
        self.gold = 20
        self.potions = 3
        self.turn = 0
        self.enemy_name = "Iana"
        self.enemy_max_hp = 85
        self.enemy_hp = 85
        self.enemy_max_mp = 40
        self.enemy_mp = 40
        self.enemy_defeated = 0
        self.guard = False
        self.battle_over = False
        self.log_lines = ["Bem-vindo, mago!", "Iana bloqueia o caminho...", "Escolha sua ação."]
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        with self.root_box.canvas.before:
            Color(*BG)
            self.bg_rect = Rectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=self._bg_update, size=self._bg_update)

        title = Label(text="[b]✦ MAGOS DO INFINITO ✦[/b]", markup=True,
                      size_hint_y=None, height=dp(42), font_size="22sp", color=CYAN)
        self.root_box.add_widget(title)

        self.status_panel = Panel(orientation="vertical", padding=dp(8), spacing=dp(4),
                                  size_hint_y=None, height=dp(118))
        self.player_label = Label(text="", markup=True, color=WHITE, halign="left",
                                  valign="middle", font_size="14sp")
        self.player_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.enemy_label = Label(text="", markup=True, color=WHITE, halign="left",
                                 valign="middle", font_size="14sp")
        self.enemy_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.status_panel.add_widget(self.player_label)
        self.status_panel.add_widget(self.enemy_label)
        self.root_box.add_widget(self.status_panel)

        self.scene = Label(text="[color=64dfff]✦[/color]     [color=ff5577]☄[/color]\n"
                                "[b]ARTHUR[/b]  VS  [b]IANA[/b]\n"
                                "[color=9ab6d9]Ruínas do Bosque Astral[/color]",
                           markup=True, font_size="19sp", color=WHITE,
                           size_hint_y=None, height=dp(94), halign="center", valign="middle")
        self.root_box.add_widget(self.scene)

        self.log_panel = Panel(orientation="vertical", padding=dp(8), size_hint_y=1)
        self.log_label = Label(text="", color=WHITE, font_size="14sp",
                               halign="left", valign="top", markup=True)
        self.log_label.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.log_label)
        self.log_panel.add_widget(scroll)
        self.root_box.add_widget(self.log_panel)

        self.action_grid = GridLayout(cols=2, spacing=dp(7), size_hint_y=None,
                                      height=dp(156), row_default_height=dp(48), row_force_default=True)
        self.buttons = []
        for label, callback in [
            ("⚔ ATACAR", self.attack),
            ("✦ MAGIA", self.magic),
            ("🧪 POÇÃO", self.potion),
            ("🛡 DEFENDER", self.defend),
            ("🎲 GOLPE DA SORTE", self.luck),
            ("↻ NOVO INIMIGO", self.new_enemy),
        ]:
            btn = PixelButton(text=label)
            btn.bind(on_release=lambda instance, cb=callback: cb())
            self.action_grid.add_widget(btn)
            self.buttons.append(btn)
        self.root_box.add_widget(self.action_grid)

        self.footer = Label(text="", color=MUTED, font_size="12sp",
                            size_hint_y=None, height=dp(24))
        self.root_box.add_widget(self.footer)
        self.refresh()
        return self.root_box

    def _bg_update(self, *_):
        self.bg_rect.pos = self.root_box.pos
        self.bg_rect.size = self.root_box.size

    def add_log(self, message):
        self.log_lines.append(message)
        self.log_lines = self.log_lines[-8:]
        self.log_label.text = "\n".join(self.log_lines)

    def refresh(self):
        self.player_label.text = (
            f"[b][color=64dfff]ARTHUR  Nv.{self.level}[/color][/b]  "
            f"HP [color=ff5577]{self.player_hp}/{self.player_max_hp}[/color]   "
            f"MP [color=5599ff]{self.player_mp}/{self.player_max_mp}[/color]\n"
            f"EXP {self.exp}/100    Moedas [color=ffcc55]{self.gold}[/color]    Poções {self.potions}"
        )
        self.enemy_label.text = (
            f"[b][color=ff6688]{self.enemy_name}[/color][/b]  "
            f"HP [color=ff5577]{self.enemy_hp}/{self.enemy_max_hp}[/color]   "
            f"MP [color=5599ff]{self.enemy_mp}/{self.enemy_max_mp}[/color]"
        )
        self.log_label.text = "\n".join(self.log_lines)
        self.footer.text = "Combate por turnos • Toque em uma ação • Protótipo 1.0"
        for b in self.buttons:
            b.disabled = self.battle_over and b.text != "↻ NOVO INIMIGO"

    def attack(self, *_):
        if self.battle_over: return
        damage = max(4, randint(10, 18) + self.level * 2 - randint(0, 5))
        self.enemy_hp = max(0, self.enemy_hp - damage)
        self.add_log(f"[color=64dfff]Arthur atacou e causou {damage} de dano![/color]")
        self.after_player_action()

    def magic(self, *_):
        if self.battle_over: return
        if self.player_mp < 12:
            self.add_log("[color=ffcc55]Mana insuficiente![/color]")
            self.enemy_turn()
            return
        self.player_mp -= 12
        damage = randint(22, 34) + self.level * 2
        self.enemy_hp = max(0, self.enemy_hp - damage)
        self.add_log(f"[color=bb88ff]BOLA ASTRAL! {damage} de dano mágico! (-12 MP)[/color]")
        self.after_player_action()

    def potion(self, *_):
        if self.battle_over: return
        if self.potions <= 0:
            self.add_log("[color=ffcc55]Você não tem poções![/color]")
            self.enemy_turn()
            return
        if self.player_hp == self.player_max_hp:
            self.add_log("Sua vida já está cheia.")
            self.enemy_turn()
            return
        self.potions -= 1
        healed = min(40, self.player_max_hp - self.player_hp)
        self.player_hp += healed
        self.add_log(f"[color=55ee99]Você recuperou {healed} HP![/color]")
        self.enemy_turn()

    def defend(self, *_):
        if self.battle_over: return
        self.guard = True
        self.add_log("[color=64dfff]Arthur ergue um escudo mágico![/color]")
        self.enemy_turn()

    def luck(self, *_):
        if self.battle_over: return
        roll = randint(1, 100)
        self.add_log(f"[color=ffcc55]Dado da sorte: {roll}/100[/color]")
        if roll >= 90:
            damage = randint(35, 55) + self.level
            self.enemy_hp = max(0, self.enemy_hp - damage)
            self.add_log(f"[color=ffcc55]CRÍTICO CÓSMICO! {damage} de dano![/color]")
            self.after_player_action()
        elif roll <= 15:
            self.player_hp = max(1, self.player_hp - 8)
            self.add_log("A sorte falhou! Você perdeu 8 HP.")
            self.enemy_turn()
        else:
            damage = randint(12, 24)
            self.enemy_hp = max(0, self.enemy_hp - damage)
            self.add_log(f"Golpe da sorte causou {damage} de dano.")
            self.after_player_action()

    def after_player_action(self):
        if self.enemy_hp <= 0:
            self.victory()
        else:
            self.enemy_turn()
        self.refresh()

    def enemy_turn(self):
        if self.battle_over: return
        if self.enemy_hp <= 0:
            self.victory()
            self.refresh()
            return
        if self.enemy_mp >= 10 and randint(1, 100) <= 38:
            self.enemy_mp -= 10
            damage = randint(12, 20) + self.enemy_defeated
            move = "Fogo Sombrio"
        else:
            damage = randint(7, 14) + self.enemy_defeated
            move = "ataque"
        if self.guard:
            damage = max(1, damage // 3)
            self.guard = False
            self.add_log("O escudo reduziu o dano!")
        self.player_hp = max(0, self.player_hp - damage)
        self.add_log(f"[color=ff6688]Iana usou {move}: -{damage} HP.[/color]")
        if self.player_hp <= 0:
            self.battle_over = True
            self.add_log("[b][color=ff5577]Você foi derrotado! Toque em NOVO INIMIGO para tentar de novo.[/color][/b]")
        self.refresh()

    def victory(self):
        if self.battle_over: return
        self.battle_over = True
        reward = randint(8, 18)
        self.gold += reward
        self.exp += 40
        self.add_log(f"[b][color=55ee99]VITÓRIA! +{reward} moedas e +40 EXP![/color][/b]")
        if self.exp >= 100:
            self.exp -= 100
            self.level += 1
            self.player_max_hp += 15
            self.player_max_mp += 8
            self.player_hp = self.player_max_hp
            self.player_mp = self.player_max_mp
            self.add_log(f"[color=ffcc55]SUBIU PARA O NÍVEL {self.level}! HP e MP aumentaram.[/color]")
        self.refresh()

    def new_enemy(self, *_):
        self.enemy_defeated += 1
        self.enemy_name = choice(["Iana", "Slime Astral", "Cavaleiro Vazio", "Corvo Arcano"])
        self.enemy_max_hp = 85 + self.enemy_defeated * 12
        self.enemy_hp = self.enemy_max_hp
        self.enemy_max_mp = 40 + self.enemy_defeated * 3
        self.enemy_mp = self.enemy_max_mp
        if self.player_hp <= 0:
            self.player_hp = max(45, self.player_max_hp // 2)
            self.player_mp = max(20, self.player_max_mp // 2)
            self.potions = max(1, self.potions)
        self.battle_over = False
        self.guard = False
        self.add_log(f"[color=ff6688]Um novo inimigo apareceu: {self.enemy_name}![/color]")
        self.refresh()

if __name__ == "__main__":
    RPGApp().run()
