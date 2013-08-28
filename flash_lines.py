import subprocess

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'benchmark-framework', 'src'))

import gdb_manager
import logger
import platform_struct
import run

del sys.modules['dbi']
sys.modules['dbi'] = __import__('dbi')

code = """    .thumb
    .globl main
    .globl exit
    .align 8
main:
    ldr r0, =0x1
    lsl r0, r0, #29
    ldr r1, =0x1
    lsl r1, r1, #12
    orr r0, r0, r1
    mov sp, r0
    bl initialise_trigger

    b benchmark
benchmark:
    bl start_trigger

    mov r0, #1
    mov r1, #1
    lsl r0, r0, #17

    b loop
    .balign 1024
    .rept {}
    nop
    .endr
loop:
{}
    sub r0, r0, r1
    bne loop

    bl stop_trigger
    bl exit
"""

arm_platform = platform_struct.Platform("arm", { 'gcc' : 'arm-none-eabi-gcc' }, { 'gcc' : '-std=c99 -g -T./platformcode/stm32vl_flash.ld -mcpu=cortex-m0 -mthumb -I./platformcode ./platformcode/exit.c ./platformcode/platformcode.c' }, "runners.arm")

offsets = range(0, 128)
sizes = range(2, 128)

def output_code(loop_offset, loop_code):
    with open('source.s', 'w') as f:
        f.write(code.format(loop_offset, loop_code))

def build_and_run(gdb_man, logger, loop_offset, loop_code, loop_size):
    output_code(loop_offset, loop_code)

    compiler_bin = arm_platform.compiler_bin_for('gcc')
    build_flags = arm_platform.build_flags_for('gcc')

    to_run = [compiler_bin]
    to_run += build_flags.split()
    to_run += ['source.s', '-o', 'binary']

    try:
        os.remove('binary')
    except OSError:
        # We don't care if the file doesn't already exist
        pass

    logger.log_info("builder", "Executing {}".format(" ".join(to_run)))
    p = subprocess.Popen(to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    make_out, make_err = p.communicate()

    if p.returncode != 0:
        logger.log_warn("builder", "Build failed!")
        logger.log_warn("builder", "{}\n{}".format(make_out.decode("utf-8"), make_err.decode("utf-8")))
        return

    run_id = logger.add_run(loop_offset, loop_size)
    run_obj = run.Run("loop", 'gcc', arm_platform, [], run_id)
    return gdb_man.read_energy('binary', run_obj)

def main():
    platforms = [arm_platform]

    logger_obj = logger.Logger(db='results.sqlite3')
    gdb_man = gdb_manager.GdbManager(platforms, logger_obj)
    if not gdb_man.sanity():
        return

    for offset in offsets:
        for size in sizes:
            logger_obj.log_info("main", "Offset is: {} Size is: {}".format(offset, size))
            loop_code = """    .rept {}-2
    nop
    .endr""".format(size)
            results = build_and_run(gdb_man, logger_obj, offset, loop_code, size)
            if results is None:
                print("Something went wrong")
                return
            logger_obj.record_results(results)

if __name__ == '__main__':
    main()
