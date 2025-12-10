from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# Dünya ölçüləri
WORLD_SIZE = 10

# Blok növləri (8 blok)
block_types = {
    'grass': ('grass', color.green, 'grass_texture'),
    'stone': ('stone', color.gray, 'stone_texture'),
    'wood': ('wood', color.brown, 'wood_texture'),
    'sand': ('sand', color.yellow, 'sand_texture'),
    'water': ('water', color.cyan, 'water_texture'),
    'lava': ('lava', color.red, 'lava_texture'),
    'diamond': ('diamond', color.cyan, 'diamond_texture'),
    'gold': ('gold', color.yellow, 'gold_texture'),
}

selected_block = 'grass'

# Envanter sinfi
class Inventory(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.slots = []
        x_offset = -0.7
        for block in block_types:
            btn = Button(texture=block_types[block][2], color=block_types[block][1], scale=0.1, position=(x_offset, -0.4))
            btn.on_click = Func(self.select_block, block)
            self.slots.append(btn)
            x_offset += 0.15
    
    def select_block(self, block_name):
        global selected_block
        selected_block = block_name

# Blok sinfi
class Voxel(Button):
    def __init__(self, position=(0,0,0), block_type='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=block_types[block_type][2],
            color=block_types[block_type][1],
            highlight_color=color.lime,
        )
        self.block_type = block_type

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                new_pos = self.position + mouse.normal
                if abs(new_pos.x) < WORLD_SIZE//2 and abs(new_pos.z) < WORLD_SIZE//2:
                    Voxel(position=new_pos, block_type=selected_block)
            if key == 'right mouse down':
                destroy(self)

# Zəmin yarat (Yalnızca yakın blokları render etme)
def create_world():
    for z in range(-WORLD_SIZE//2, WORLD_SIZE//2):
        for x in range(-WORLD_SIZE//2, WORLD_SIZE//2):
            block_type = random.choice(list(block_types.keys()))
            Voxel(position=(x, 0, z), block_type=block_type)

# Performans optimizasyonu: Gereksiz nesneleri silme
def optimize_world():
    for voxel in scene.children:
        if isinstance(voxel, Voxel):
            if (abs(voxel.position.x - player.x) > WORLD_SIZE or abs(voxel.position.z - player.z) > WORLD_SIZE):
                destroy(voxel)

# Dünya yaratma ve ilk başta yüklenmesi
create_world()

player = FirstPersonController()
player.cursor.visible = False

# Kamera rejimi dəyişmə funksiyası
third_person = True

def toggle_camera():
    global third_person
    third_person = not third_person
    if third_person:
        player.position = (player.x, player.y + 2, player.z - 5)
        player.rotation_x = 15
    else:
        player.position = (player.x, player.y, player.z)
        player.rotation_x = 0

# Kamera dəyişmə düyməsi
inventory = Inventory()

# Hata yakalama ve uyarı ekrana basma
def show_error_alert(message):
    alert = Text(message, color=color.red, scale=2, position=(0, 0))
    invoke(alert.delete, delay=3)  # 3 saniye sonra uyarıyı sil

# Ana input fonksiyonu
def input(key):
    if key == 'p':
        toggle_camera()

    # 1-8 tuşlarıyla blok seçimi
    block_keys = ['1', '2', '3', '4', '5', '6', '7', '8']
    block_names = list(block_types.keys())

    for i, key in enumerate(block_keys):
        if key == key:
            global selected_block
            selected_block = block_names[i]
            print(f"Selected block: {selected_block}")

# Performans optimizasyonu ve render için ana döngü
def update():
    optimize_world()

try:
    app.run()
except Exception as e:
    print(f"Error: {e}")
    show_error_alert("An error occurred, please check the console!")
