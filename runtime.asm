; Copyright 2025 Massimo Guarnieri
;
; Assembly program for the Thymio
; The program invokes a native function when specific variables are written in data space

    dc end_toc              ; total size of event handler table
    dc _ev.init, init       ; id and address of init event
end_toc:

func:     equ _userdata+0
n_args:   equ _userdata+1
args:     equ _userdata+2
trigger:  equ _userdata+6
iterator: equ _userdata+7

init:                       ; code executed on init event
    push 0
    store trigger

check_trigger:
    load trigger
    push 1
    jump.if.not eq check_trigger

init_loop_iterator:
    push 0
    store iterator

check_loop_iterator:
    load iterator
    load n_args
    jump.if.not lt invoke_leds_top

push_arg:
    load iterator
    push args
    add

increment_loop_iterator:
    load iterator
    push 1
    add
    store iterator
    jump check_loop_iterator

invoke_leds_top:
    push _nf.leds.top
    load func
    jump.if.not eq invoke_leds_bottom_left
    callnat _nf.leds.top
    jump end_invoke

invoke_leds_bottom_left:
    push _nf.leds.bottom.left
    load func
    jump.if.not eq invoke_leds_bottom_right
    callnat _nf.leds.bottom.left
    jump end_invoke

invoke_leds_bottom_right:
    push _nf.leds.bottom.right
    load func
    jump.if.not eq end_invoke
    callnat _nf.leds.bottom.right
    jump end_invoke

end_invoke:
    push 0
    store trigger
    jump check_trigger

    stop                    ; stop program\