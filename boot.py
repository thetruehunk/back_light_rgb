import esp
import gc
import wireless
import webrepl

esp.osdebug(0)
wireless.activate()
gc.collect()
webrepl.start()

