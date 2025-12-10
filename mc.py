from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# Dünya ölçüləri
WORLD_SIZE = 20  # Dünyanı biraz böyütdük

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

# Səs effektləri
shoot_sound = Audio('assets/punch_sound', loop=False, autoplay=False) # Varsayılan olaraq əlavə edildi

# Gökyüzü
sky = Sky()

# El (Hand) sinfi - Vizual görünüş üçün
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            scale=(0.2, 0.4),
            position=(0.5, -0.6),
            rotation=(150, -10, 0),
            color=color.white,
            texture='wood_texture' 
        )

    def active(self):
        self.position = (0.4, -0.5)
        self.rotation = (150, -10, 0)

    def passive(self):
        self.position = (0.5, -0.6)
        self.rotation = (150, -10, 0)
        
    def swing(self):
        self.animate_position((0.4, -0.5), duration=0.1, curve=curve.linear)
        self.animate_rotation((140, -10, 0), duration=0.1, curve=curve.linear)
        invoke(self.passive, delay=0.1)

# Envanter sinfi
class Inventory(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.slots = []
        x_offset = -0.7
        for block in block_types:
            btn = Button(texture=block_types[block][2], color=block_types[block][1], scale=0.08, position=(x_offset, -0.42))
            btn.on_click = Func(self.select_block, block)
            self.slots.append(btn)
            x_offset += 0.1
    
    def select_block(self, block_name):
        global selected_block
        selected_block = block_name
        # Seçilən bloku vizual olaraq göstər (El rəngini dəyiş)
        hand.color = block_types[block_name][1]
        hand.texture = block_types[block_name][2]

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
                hand.swing()
                if shoot_sound: shoot_sound.play()
                new_pos = self.position + mouse.normal
                # Yalnız dünya sərhədləri daxilində tik
                if abs(new_pos.x) < WORLD_SIZE and abs(new_pos.z) < WORLD_SIZE:
                    Voxel(position=new_pos, block_type=selected_block)
            
            if key == 'right mouse down':
                hand.swing()
                if shoot_sound: shoot_sound.play()
                destroy(self)

# Zəmin yarat (Yalnızca yakın blokları render etme)
def create_world():
    # Bedrock (yıxılmamaq üçün alt qat)
    for z in range(-WORLD_SIZE, WORLD_SIZE):
        for x in range(-WORLD_SIZE, WORLD_SIZE):
            Voxel(position=(x, -1, z), block_type='stone')

    # Random üst qat
    for z in range(-WORLD_SIZE//2, WORLD_SIZE//2):
        for x in range(-WORLD_SIZE//2, WORLD_SIZE//2):
            block_type = random.choice(list(block_types.keys()))
            if random.random() > 0.5: # Hər yerdə blok olmasın
                Voxel(position=(x, 0, z), block_type=block_type)

# Performans optimizasyonu: Gereksiz nesneleri gizləmə (silmək yerinə)
def optimize_world():
    for voxel in scene.children:
        if isinstance(voxel, Voxel):
            dist = distance(voxel.position, player.position)
            # Sadəcə uzaqdakı blokları görünməz et, silmə
            if dist > 15:
                voxel.enabled = False
            else:
                voxel.enabled = True

# Dünya yaratma ve ilk başta yüklenmesi
create_world()

player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.jump_height = 2

hand = Hand()

# Kamera rejimi dəyişmə funksiyası
third_person = False

def toggle_camera():
    global third_person
    third_person = not third_person
    if third_person:
        camera.z = -3 # Kameranı geri çək
        camera.y = 1
    else:
        camera.z = 0  # Kameranı yerinə qaytar
        camera.y = 0

# Kamera dəyişmə düyməsi
inventory = Inventory()

# Hata yakalama ve uyarı ekrana basma
def show_error_alert(message):
    alert = Text(message, color=color.red, scale=2, position=(-0.1, 0))
    invoke(alert.delete, delay=3)  # 3 saniye sonra uyarıyı sil

# Ana input fonksiyonu
def input(key):
    if key == 'p':
        toggle_camera()
    
    if key == 'escape':
        quit()

    # 1-8 tuşlarıyla blok seçimi
    block_keys = ['1', '2', '3', '4', '5', '6', '7', '8']
    block_names = list(block_types.keys())

    if key in block_keys:
        i = block_keys.index(key)
        inventory.select_block(block_names[i])
        print(f"Selected block: {block_names[i]}")

# Performans optimizasyonu ve render için ana döngü
def update():
    # Optimizasiyanı hər frame çağırmaq ağır ola bilər, hər 10 framdən bir çağır
    if frame_index % 10 == 0:
        optimize_world()
        
    # Oyunçunun düşməsini əngəllə
    if player.y < -10:
        player.position = (0, 2, 0)

try:
    app.run()
except Exception as e:
    print(f"Error: {e}")
    show_error_alert("An error occurred, please check the console!")
