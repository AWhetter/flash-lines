#ifndef __PLATFORMCODE_H__
#define __PLATFORMCODE_H__

#ifndef REPEAT_FACTOR
#define REPEAT_FACTOR   (4096)
#endif

#include "exit.h"

extern void initialise_trigger();
extern void stop_trigger();
extern void start_trigger();

#endif /* __PLATFORMCODE_H__ */
