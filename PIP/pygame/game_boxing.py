# Мини версия игры Boxing


import pygame,sys,random,math
pygame.init()
W,H=640,480
s=pygame.display.set_mode((W,H))
c=pygame.time.Clock()
f=pygame.font.SysFont(None,24)
ph,eh=100,100
cdp,atk=0,0
pf=[{'r':60,'x':W//2-120,'y':H-80,'st':0},{'r':60,'x':W//2+120,'y':H-80,'st':0}]
ef=[{'r':40,'x':W//2-60,'y':H//2+120,'st':0},{'r':40,'x':W//2+60,'y':H//2+120,'st':0}]
fx,fy,ft,t=0,0,0,0
fsx,fsy,shx,shy=0,0,0,0
pl,pr={'x':0,'y':0},{'x':0,'y':0}
scs,pscs=[],[]
def dr():
    ox,oy=shx,shy
    s.fill((0,0,0))
    pygame.draw.rect(s,(255,0,0),(50+ox,30+oy,ph*2,20))
    pygame.draw.rect(s,(0,255,0),(W-250+ox,30+oy,eh*2,20))
    cx,cy=W//2+fx+fsx+ox,H//2+fy+fsy+oy
    pygame.draw.circle(s,(255,220,200),(cx,cy),120)
    for sx,sy,l,a in scs:
        ex,ey=cx+sx+math.cos(a)*l,cy+sy+math.sin(a)*l
        pygame.draw.line(s,(150,0,0),(cx+sx,cy+sy),(ex,ey),2)
    exs,eys=fx//5,fy//5
    el,er=(cx-40+exs,cy-40+eys),(cx+40+exs,cy-40+eys)
    pygame.draw.circle(s,(0,0,0),el,20);pygame.draw.circle(s,(0,0,0),er,20)
    pygame.draw.circle(s,(255,255,255),(int(el[0]+pl['x']),int(el[1]+pl['y'])),5)
    pygame.draw.circle(s,(255,255,255),(int(er[0]+pr['x']),int(er[1]+pr['y'])),5)
    pygame.draw.rect(s,(0,0,0),(cx-50+exs,cy+40+eys,100,20))
    for q in ef:pygame.draw.circle(s,(200,50,50),(q['x']+ox,q['y']+oy),q['r'])
    for q in pf:pygame.draw.circle(s,(200,200,200),(q['x']+ox,q['y']+oy),q['r'])
    for sx,sy,l,a in pscs:
        ex,ey=sx+math.cos(a)*l,sy+math.sin(a)*l
        pygame.draw.line(s,(255,50,50),(sx,sy),(ex,ey),3)
    s.blit(f.render(f"P:{ph} E:{eh}",1,(255,255,255)),(W//2-40+ox,5+oy))
    pygame.display.flip()
def punch():
    global fsx,fsy,scs
    q=random.choice(pf);q.update({'r':90,'x':W//2+random.randint(-40,40),'y':H//2+random.randint(-40,40),'st':1})
    fsx,fsy=random.randint(-q['r'],q['r']),random.randint(-q['r']//2,q['r']//2)
    scs.append((random.randint(-100,100),random.randint(-100,100),random.randint(10,40),random.uniform(0,6.28)))
def eatk():
    global ph,shx,shy,pscs
    q=random.choice(ef);q.update({'r':120,'y':H//2+30,'st':1})
    ph=max(0,ph-q['r']//10)
    shx,shy=random.randint(-q['r']//2,q['r']//2),random.randint(-q['r']//2,q['r']//2)
    for _ in range(random.randint(1,3)):
        sx,sy,l,ang=random.randint(0,W),random.randint(0,H),random.randint(80,200),random.uniform(-.5,.5)
        pscs.append((sx,sy,l,ang))
while 1:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:pygame.quit();sys.exit()
        if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE and cdp==0:punch();cdp=20
    if cdp>0:cdp-=1
    if t==0:ft={'x':random.choice([-30,0,30]),'y':random.choice([-20,0,10])};t=random.randint(20,40)
    else:fx+=(ft['x']-fx)//10;fy+=(ft['y']-fy)//10;t-=1
    fsx//=2;fsy//=2;shx//=2;shy//=2
    pl['x']+=(-fx//5-pl['x'])//5;pl['y']+=(-fy//5-pl['y'])//5
    pr['x']+=(-fx//5-pr['x'])//5;pr['y']+=(-fy//5-pr['y'])//5
    for i,q in enumerate(pf):
        if q['st']:q['r']-=5;q['y']+=4
        else:
            ix=W//2-120 if i==0 else W//2+120
            if q['r']<60:q['r']+=2
            if q['y']<H-80:q['y']+=2
            q['x']+=(ix-q['x'])//5
        if q['st'] and q['r']<=30:
            eh=max(0,eh-max(5,25-q['r']));q['st']=0
    for i,q in enumerate(ef):
        if q['st']:q['r']-=3;q['y']+=2
        else:
            ix=W//2-60 if i==0 else W//2+60
            if q['r']<40:q['r']+=2
            if q['y']<H//2+120:q['y']+=2
            q['x']+=(ix-q['x'])//5
        if q['st'] and q['r']<=40:q['st']=0
    atk+=1
    if atk>60:eatk();atk=0
    dr()
    if ph<=0 or eh<=0:
        m="Win!"if eh<=0 else"Lose!"
        s.fill((0,0,0));s.blit(f.render(m,1,(255,255,255)),(W//2-20,H//2));pygame.display.flip();pygame.time.wait(2000)
        ph,eh=100,100;pf=[{'r':60,'x':W//2-120,'y':H-80,'st':0},{'r':60,'x':W//2+120,'y':H-80,'st':0}]
        ef=[{'r':40,'x':W//2-60,'y':H//2+120,'st':0},{'r':40,'x':W//2+60,'y':H//2+120,'st':0}]
        fx,fy,ft,t,fsx,fsy,shx,shy,pl,pr,scs,pscs,atk=0,0,{'x':0,'y':0},0,0,0,0,0,{'x':0,'y':0},{'x':0,'y':0},[],[],0
    c.tick(30)
