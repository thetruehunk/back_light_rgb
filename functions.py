import machine
import gc
import uasyncio as asyncio
import ubinascii
import ujson as json
import utime as time


def load_config(config_file):
    try:
        with open(config_file) as f:
            config = json.load(f)
        return config

    except OSError:
       print("No such config file:", config_file)
       time.sleep(5)
       machine.reset()

    except ValueError:
       print("This is not a valid json file:", config_file)
       time.sleep(5)
       machine.reset()


def save_config(config, config_file):
   try:
     with open(config_file, "w") as f:
         json.dump(config, f)

   except:
     pass


async def feed_watchdog(wdt):
    while True:
        wdt.feed()
        await asyncio.sleep(1)


async def memory_state(syslog):
    while True:
        free = gc.mem_free()
        alloc = gc.mem_alloc()
        total = free + alloc
        used = "{0:.2f}%".format(free/total*100)
        syslog.info("Memory state: total:{0} free:{1} ({2})".format(total,free,used))
        await asyncio.sleep(60)


def set_color(np, hex_color):
    color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    for i in range(60):
        np[i] = color
    np.write()


def set_color_handler(qs, np):
    config = load_config("config.json")
    h = qs.split('=')[1].replace('%23', '')
    set_color(np, h)
    config["DEFAULT_COLOR"] = h
    save_config(config, "config.json")


def set_config_handler(qs):
    config = load_config("config.json")
    param = qs.split('&')
    for item in param:
        key, value = item.split('=')
        config[key] = value
    save_config(config, 'config.json')


def require_auth(func):
    config = load_config('config.json')
    def auth(req, resp):
        auth = req.headers.get(b"Authorization")
        if not auth:
            yield from resp.awrite(
                "HTTP/1.0 401 NA\r\n"
                'WWW-Authenticate: Basic realm="Picoweb Realm"\r\n'
                "\r\n"
            )
            return

        auth = auth.split(None, 1)[1]
        auth = ubinascii.a2b_base64(auth).decode()
        req.username, req.passwd = auth.split(":", 1)
        if not (
            (req.username == config["WEB-LOGIN"])
            and (req.passwd == config["WEB-PASSWORD"])
        ):
            yield from resp.awrite(
                "HTTP/1.0 401 NA\r\n"
                'WWW-Authenticate: Basic realm="Picoweb Realm"\r\n'
                "\r\n"
            )
            return

        yield from func(req, resp)

    return auth

