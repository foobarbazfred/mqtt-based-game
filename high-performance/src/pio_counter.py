#
#  file: pio_counter.py
#
#  counter by PIO w/ chattering filter
#  v0.01  1st version 
#  v0.02  refactor (not jmp but wait)
#  v0.03  bug fix (convert number; minus -> plus is fixed)
#  v0.04  rafctor as library
#

import time 
import machine
from machine import Pin
import rp2 


# The system clock is set to 125MHz for compatibility 
# with both RP2040 and RP2450 microcontrollers.
machine.freq(125_000_000)  # set system clock 125MHz


@rp2.asm_pio(set_init = rp2.PIO.OUT_HIGH)
def pin_wait():

    # _init
    set(x, 0)         # clear x(counter) 

    # _loop_begin
    label('_loop_begin')
    set(y, 24)         # const for wait counter (25msec (24 + 1))

    # wait until in_pin is H
    wait(1, pin, 0)   # wait until in_pin H(1) (in_pin + offset 0)
    set(pins, 0)

    # wait until in_pin is  L
    wait(0, pin, 0)   # wait until in_pin L(0) (in_pin + offset 0)
    set(pins, 1)  # LOW is effective

    #
    # Triggerd( H->L ), so decrement X(counter)
    #
    jmp(x_dec, '_wait_for_y_ms')  # -1 -> -2 -> .... -N

    # SM will not output FIFO , machine should execute by ASM   
    #mov(isr, x)      # not mov  by State machine so  execute it by CPU
    #push(noblock)    # not push by State machine so execute it by CPU

    #
    # to avoid chattering so wait for y+1 ms
    #
    #_wait_for_y_ms   (wait for Y+1 (ms))
    label('_wait_for_y_ms')
    jmp(y_dec, '_wait_for_y_ms').delay(1)  # wait for 1ms * ( counter(Y) +1 )

    # jump to _loop_begin
    jmp('_loop_begin')

    # end of loop


CODE_MOV_ISR = rp2.asm_pio_encode("mov(isr, x)", 0)
CODE_PUSH = rp2.asm_pio_encode("push(noblock)", 0)

def _push_to_fifo():
    #sm.exec("mov(isr, x)")     # 0xe080
    #sm.exec("push(noblock)")   # 0x80a0
    sm.exec(CODE_MOV_ISR)
    sm.exec(CODE_PUSH)


def get_counter():
    counter = 0
    if sm.rx_fifo() == 0:
        _push_to_fifo()
        if sm.rx_fifo() == 0:
            print('Internal Error in pio_counter')
            return None
    counter = sm.get()
    if counter == 0:
        pass
    else:
        # convert negative count vale to positive
        counter = 0x1_0000_0000 - counter  
    return counter




# Instantiate a state machine with the blink program, 
# at 2000Hz, with set bound to Pin(16) 

in_pin = Pin(0, Pin.IN, Pin.PULL_UP)
sm = rp2.StateMachine(0, pin_wait, freq=2_000, in_base=in_pin, set_base=Pin(16))   # 2KHz
sm.active(1) 



#  
#  prev_count = 0
#  while True:
#      if sm.rx_fifo() == 0:
#          #sm.exec("mov(isr, x)")     # 0xe080
#          #sm.exec("push(noblock)")   # 0x80a0
#          sm.exec(CODE_MOV_ISR)
#          sm.exec(CODE_PUSH)
#      else:
#          count = sm.get()
#          if count != 0:
#              count = 0x1_0000_0000 - count
#          if prev_count != count:
#              print(count)
#              prev_count = count
#  
#  
#  time.sleep(5)
#  sm.active(0)
#  



#
# https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.html#rp2.asm_pio
# https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.html#rp2.asm_pio
#
