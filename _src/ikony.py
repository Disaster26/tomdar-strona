# favicon.ico i apple-touch-icon.png narysowane w Pillow tym samym kształtem co favicon.svg (rama + krzesło)
from PIL import Image, ImageDraw
def rysuj(n):
    s=n/64; im=Image.new('RGB',(n,n),'white'); d=ImageDraw.Draw(im)
    w=max(1,round(6*s))
    d.line([(5*s,5*s),(55*s,5*s)],fill='#FDC506',width=w); d.line([(55*s,5*s-w/2),(55*s,30*s)],fill='#FDC506',width=w)
    d.line([(5*s,5*s-w/2),(5*s,52*s)],fill='#FDC506',width=w); d.line([(5*s-w/2,52*s),(34*s,52*s)],fill='#FDC506',width=w)
    k=lambda x,y:((31+(x-188)*.62)*s,(12+(y-21)*.62)*s)
    d.polygon([k(203,21.5),k(236,21.5),k(235.6,25.7),k(203.4,25.7)],fill='black')
    for x0,x1 in [(204,207.2),(210.6,213),(216.6,219),(222.6,225)]:
        d.polygon([k(x0,24),k(x1,24),k(x1,64),k(x0,64)],fill='black')
    d.polygon([k(232.2,23.6),k(235.6,23.6),k(233.8,100),k(230.4,100)],fill='black')
    d.polygon([k(188,62.5),k(234.8,62.5),k(234.8,67.9),k(190.2,70.3)],fill='black')
    d.polygon([k(191,69.6),k(194.6,69.6),k(192.8,99),k(189.4,99)],fill='black')
    d.polygon([k(204.6,68.8),k(207.6,68.8),k(207.9,90.8),k(205.1,90.8)],fill='black')
    return im
big=rysuj(512)
big.resize((180,180),Image.LANCZOS).save('apple-touch-icon.png',optimize=True)
big.resize((48,48),Image.LANCZOS).save('favicon.ico',sizes=[(16,16),(32,32),(48,48)])
print('ok')
