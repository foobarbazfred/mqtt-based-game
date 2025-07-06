#
# UI for MQTT Game Renad OH
#
import time

def np_clear(np):
    for i in range(len(np)):
       np[i]=(0, 0, 0)
    np.write()

def np_light_neo(np, ptn):
    size = len(np)
    if ptn == '3p':
        for i in range(0,3):
            np[int(size * i / 3)]=(0x08,0,0)
    elif ptn == 'c3':
        for i in range(int(size * 1 / 3)):
            np[i]=(0x0, 0x8, 0x0)
    elif ptn == 'c2':
        for i in range(int(size * 2 / 3)):
            np[i]=(0x0, 0x8, 0x0)
    elif ptn == 'c1':
        for i in range(int(size * 3 / 3)):
            np[i]=(0x0, 0x8, 0x0)
    elif ptn == 'c0':
        for i in range(int(size/1)):
            np[i]=(0x0, 0x0, 0x08)
    np.write()

CLICK_LIMIT = 100
def np_light_progress(np, p0, p1):
    np_clear(np)
    if p0 + p1 < CLICK_LIMIT:
       space = CLICK_LIMIT - p0 - p1
    else:
       space = 0
    length = len(np)

    p0_n = int(length / (p0 + p1 + space) * p0)
    sp_n = int(length / (p0 + p1 + space) * space)
    p1_n = int(length / (p0 + p1 + space) * p1)

    for i in range(p0_n):
        np[i]=(0, 08, 0)
    for i in range(sp_n):
        np[p0_n + i]=(0, 0, 0)
    for i in range(p1_n):
        np[p0_n + sp_n + i]=(08, 08, 0)

    # set RED marker
    if p0 > CLICK_LIMIT/2:
       np[p0_n] = (8,0,0)
    elif p1 > CLICK_LIMIT/2:
       np[p0_n+sp_n] = (8,0,0)
    else:
       np[int(length/2)] = (8,0,0)

    np.write()


#
# play sound
#


def play_sound(buzzer, type):

    if type == 'c3'  or type == 'c2' or type == 'c1':
       buzzer.freq(700)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 

    elif type == 'c0':
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 

    elif type == 'loser':
       buzzer.freq(650)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.duty_u16(32768) 
       time.sleep(0.5)
       buzzer.duty_u16(0) 


    elif type == 'winner':
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.freq(1200)
       buzzer.duty_u16(32768) 
       time.sleep(0.5)
       buzzer.duty_u16(0) 


#
#
#


