# Минималистичная игра с бесконечным количеством уровней.
# * Игрок собирает ключи и открывает дверь для перехода на следующий уровень.
# * Враги умные и идут к игроку, но не появляются рядом с ним.
# * Стены блокируют движение игроков и врагов.
# * Каждый уровень рандомный, с +1 врагом и +1 ключом на новом уровне.

# pip install pygame


import pygame,sys,random,math
pygame.init()
W,H=640,480
sc=pygame.display.set_mode((W,H))
clk=pygame.time.Clock()
font=pygame.font.SysFont(None,36)

level = 1
MIN_DIST = 150

def new_level(level):
    player = pygame.Rect(50,50,30,30)
    walls=[]
    for _ in range(10):
        w=pygame.Rect(random.randint(0,W-100),random.randint(0,H-100),
                      random.randint(50,150),random.randint(20,50))
        if w.colliderect(player): continue
        walls.append(w)
    door = pygame.Rect(W-60,H-80,40,60)
    keys = []
    for _ in range(level):
        while True:
            k = pygame.Rect(random.randint(0,W-20),random.randint(0,H-20),20,20)
            if any(k.colliderect(w) for w in walls) or k.colliderect(player) or k.colliderect(door): continue
            keys.append(k); break
    enemies=[]
    for _ in range(level+1):
        while True:
            e = pygame.Rect(random.randint(0,W-30),random.randint(0,H-30),30,30)
            if any(e.colliderect(w) for w in walls) or e.colliderect(player) or e.colliderect(door) or any(e.colliderect(k) for k in keys): continue
            if math.hypot(e.x - player.x, e.y - player.y) < MIN_DIST: continue
            enemies.append(e); break
    return player, walls, door, keys, enemies

player, walls, door, keys, enemies = new_level(level)
got_keys = 0; game_over=False

def move_rect(rect, dx, dy):
    rect.x += dx
    if any(rect.colliderect(w) for w in walls): rect.x -= dx
    rect.y += dy
    if any(rect.colliderect(w) for w in walls): rect.y -= dy

def draw():
    sc.fill((20,20,30))
    pygame.draw.rect(sc,(0,200,0),player)
    for e in enemies: pygame.draw.rect(sc,(200,50,50),e)
    for w in walls: pygame.draw.rect(sc,(100,100,100),w)
    for k in keys: pygame.draw.rect(sc,(255,255,0),k)
    pygame.draw.rect(sc,(150,75,0),door)
    sc.blit(font.render(f"Level: {level} Keys: {got_keys}/{len(keys)}",1,(255,255,255)),(10,10))
    if game_over: sc.blit(font.render("Game Over",1,(255,0,0)),(W//2-80,H//2))
    pygame.display.flip()

while True:
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT: pygame.quit();sys.exit()
    if not game_over:
        keys_pressed=pygame.key.get_pressed()
        dx=(keys_pressed[pygame.K_RIGHT]-keys_pressed[pygame.K_LEFT])*4
        dy=(keys_pressed[pygame.K_DOWN]-keys_pressed[pygame.K_UP])*4
        move_rect(player, dx, dy)
        for e in enemies:
            ex,ey = 0,0
            if e.x < player.x: ex=2
            elif e.x > player.x: ex=-2
            if e.y < player.y: ey=2
            elif e.y > player.y: ey=-2
            move_rect(e, ex, ey)
            if e.colliderect(player): game_over=True
        for k in keys[:]:
            if player.colliderect(k):
                keys.remove(k); got_keys+=1
        if player.colliderect(door) and got_keys==level:
            level+=1
            player, walls, door, keys, enemies = new_level(level)
            got_keys=0
    draw()
    clk.tick(30)
