import gc
from machine import Pin, WDT
import picoweb
from neopixel import NeoPixel
import usyslog
import uasyncio as asyncio
from functions import (load_config,
                       feed_watchdog,
                       memory_state,
                       set_config_handler,
                       set_color,
                       set_color_handler,
                       require_auth)
from wireless import check_connection

config = load_config("config.json")

syslog = usyslog.UDPClient(ip=config["SYSLOG-SERVER-IP"])

app = picoweb.WebApp(__name__)

np = NeoPixel(Pin(4), 60)

wdt = WDT()
wdt.feed()

set_color(np, config["DEFAULT_COLOR"])


@app.route("/")
@require_auth
def send_index(req, resp):
    syslog.info("Picoweb: requested page 'index.html'")
    gc.collect()
    config = load_config("config.json")
    yield from app.render_template(resp, "/index.html", (config,))


@app.route("/config")
@require_auth
def get_config(req, resp):
    syslog.info("Picoweb: requested page 'config.html'")
    gc.collect()
    config = load_config("config.json")
    yield from app.render_template(resp, "config.html", (config,))


@app.route("/set_config")
@require_auth
def set_config(req, resp):
    syslog.info("Picoweb: configuration change request received")
    gc.collect()
    if req.method == "GET":
        set_config_handler(req.qs)
        headers = {"Location": "/config"}
        yield from picoweb.start_response(resp, status="303", headers=headers)
    else:
        pass


@app.route("/set_color")
def set_color(req, resp):
    syslog.info("Picoweb: color change request received")
    gc.collect()
    if req.method == "GET":
        set_color_handler(req.qs, np)
        headers = {"Location": "/"}
        yield from picoweb.start_response(resp, status="303", headers=headers)
    else:
        pass

loop = asyncio.get_event_loop()
loop.create_task(check_connection())
loop.create_task(feed_watchdog(wdt))
loop.create_task(memory_state(syslog))

app.run(debug=True, host="0.0.0.0", port=80)

