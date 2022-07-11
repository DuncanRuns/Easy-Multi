import win32con

TRANSLATIONS_TO_GLFW = {
    "key.keyboard.unknown": -1,
    "key.mouse.left": 0,
    "key.mouse.right": 1,
    "key.mouse.middle": 2,
    "key.mouse.4": 3,
    "key.mouse.5": 4,
    "key.mouse.6": 5,
    "key.mouse.7": 6,
    "key.mouse.8": 7,
    "key.keyboard.0": 48,
    "key.keyboard.1": 49,
    "key.keyboard.2": 50,
    "key.keyboard.3": 51,
    "key.keyboard.4": 52,
    "key.keyboard.5": 53,
    "key.keyboard.6": 54,
    "key.keyboard.7": 55,
    "key.keyboard.8": 56,
    "key.keyboard.9": 57,
    "key.keyboard.a": 65,
    "key.keyboard.b": 66,
    "key.keyboard.c": 67,
    "key.keyboard.d": 68,
    "key.keyboard.e": 69,
    "key.keyboard.f": 70,
    "key.keyboard.g": 71,
    "key.keyboard.h": 72,
    "key.keyboard.i": 73,
    "key.keyboard.j": 74,
    "key.keyboard.k": 75,
    "key.keyboard.l": 76,
    "key.keyboard.m": 77,
    "key.keyboard.n": 78,
    "key.keyboard.o": 79,
    "key.keyboard.p": 80,
    "key.keyboard.q": 81,
    "key.keyboard.r": 82,
    "key.keyboard.s": 83,
    "key.keyboard.t": 84,
    "key.keyboard.u": 85,
    "key.keyboard.v": 86,
    "key.keyboard.w": 87,
    "key.keyboard.x": 88,
    "key.keyboard.y": 89,
    "key.keyboard.z": 90,
    "key.keyboard.f1": 290,
    "key.keyboard.f2": 291,
    "key.keyboard.f3": 292,
    "key.keyboard.f4": 293,
    "key.keyboard.f5": 294,
    "key.keyboard.f6": 295,
    "key.keyboard.f7": 296,
    "key.keyboard.f8": 297,
    "key.keyboard.f9": 298,
    "key.keyboard.f10": 299,
    "key.keyboard.f11": 300,
    "key.keyboard.f12": 301,
    "key.keyboard.f13": 302,
    "key.keyboard.f14": 303,
    "key.keyboard.f15": 304,
    "key.keyboard.f16": 305,
    "key.keyboard.f17": 306,
    "key.keyboard.f18": 307,
    "key.keyboard.f19": 308,
    "key.keyboard.f20": 309,
    "key.keyboard.f21": 310,
    "key.keyboard.f22": 311,
    "key.keyboard.f23": 312,
    "key.keyboard.f24": 313,
    "key.keyboard.f25": 314,
    "key.keyboard.num.lock": 282,
    "key.keyboard.keypad.0": 320,
    "key.keyboard.keypad.1": 321,
    "key.keyboard.keypad.2": 322,
    "key.keyboard.keypad.3": 323,
    "key.keyboard.keypad.4": 324,
    "key.keyboard.keypad.5": 325,
    "key.keyboard.keypad.6": 326,
    "key.keyboard.keypad.7": 327,
    "key.keyboard.keypad.8": 328,
    "key.keyboard.keypad.9": 329,
    "key.keyboard.keypad.add": 334,
    "key.keyboard.keypad.decimal": 330,
    "key.keyboard.keypad.enter": 335,
    "key.keyboard.keypad.equal": 336,
    "key.keyboard.keypad.multiply": 332,
    "key.keyboard.keypad.divide": 331,
    "key.keyboard.keypad.subtract": 333,
    "key.keyboard.down": 264,
    "key.keyboard.left": 263,
    "key.keyboard.right": 262,
    "key.keyboard.up": 265,
    "key.keyboard.apostrophe": 39,
    "key.keyboard.backslash": 92,
    "key.keyboard.comma": 44,
    "key.keyboard.equal": 61,
    "key.keyboard.grave.accent": 96,
    "key.keyboard.left.bracket": 91,
    "key.keyboard.minus": 45,
    "key.keyboard.period": 46,
    "key.keyboard.right.bracket": 93,
    "key.keyboard.semicolon": 59,
    "key.keyboard.slash": 47,
    "key.keyboard.space": 32,
    "key.keyboard.tab": 258,
    "key.keyboard.left.alt": 342,
    "key.keyboard.left.control": 341,
    "key.keyboard.left.shift": 340,
    "key.keyboard.left.win": 343,
    "key.keyboard.right.alt": 346,
    "key.keyboard.right.control": 345,
    "key.keyboard.right.shift": 344,
    "key.keyboard.right.win": 347,
    "key.keyboard.enter": 257,
    "key.keyboard.escape": 256,
    "key.keyboard.backspace": 259,
    "key.keyboard.delete": 261,
    "key.keyboard.end": 269,
    "key.keyboard.home": 268,
    "key.keyboard.insert": 260,
    "key.keyboard.page.down": 267,
    "key.keyboard.page.up": 266,
    "key.keyboard.caps.lock": 280,
    "key.keyboard.pause": 284,
    "key.keyboard.scroll.lock": 281,
    "key.keyboard.menu": 348,
    "key.keyboard.print.screen": 283,
    "key.keyboard.world.1": 161,
    "key.keyboard.world.2": 162
}


def get_vk_from_glfw(key: int) -> int:
    if key <= 7 and key >= -1:  # Unknown or Mouse
        return -1
    if key <= 57 and key >= 48:  # Number
        return key
    if key >= 65 and key <= 90:  # Letter
        return key
    if key >= 290 and key <= 313:  # Function keys
        return key - 290 + win32con.VK_F1
    if key == 282:  # Num Lock
        return win32con.VK_NUMLOCK
    if key >= 320 and key <= 329:  # Num keys
        return key - 320 + win32con.VK_NUMPAD0
    if key == 334:  # Add key
        return win32con.VK_ADD
    if key == 330:  # Decimal key
        return win32con.VK_DECIMAL
    if key == 335:  # Numpad enter key
        return win32con.VK_RETURN  # definitely wrong lol
    if key == 336:  # Equals (on numpad) key
        return 0xBB  # definitely wrong lol
    if key == 332:  # Multiply key
        return win32con.VK_MULTIPLY
    if key == 331:  # Divide key
        return win32con.VK_DIVIDE
    if key == 333:  # Subtract key
        return win32con.VK_SUBTRACT
    if key == 264:  # Down key
        return win32con.VK_DOWN
    if key == 263:  # Left key
        return win32con.VK_LEFT
    if key == 262:  # Right key
        return win32con.VK_RIGHT
    if key == 265:  # Up key
        return win32con.VK_UP
    if key == 39:  # Apostrophe
        return 0xDE  # May be wrong
    if key == 92:  # Backslash
        return 0xDC  # May be wrong
    if key == 44:  # ,< key
        return 0xBC  # May be wrong
    if key == 61:  # += key
        return 0xBB  # May be wrong
    if key == 96:  # `~ key
        return 0xC0  # May be wrong
    if key == 91:  # [{ key
        return 0xDB  # May be wrong
    if key == 45:  # -_ key
        return 0xBD  # May be wrong
    if key == 46:  # .> key
        return 0xBE  # May be wrong
    if key == 93:  # ]} key
        return 0xDD  # May be wrong
    if key == 59:  # ;: key
        return 0xBA  # May be wrong
    if key == 47:  # /? key
        return 0xBF  # May be wrong
    if key == 32:  # Space
        return win32con.VK_SPACE
    if key == 258:  # Tab
        return win32con.VK_TAB
    if key == 342:  # Left alt
        return win32con.VK_LMENU
    if key == 341:  # Left ctrl
        return win32con.VK_LCONTROL
    if key == 340:  # Left shift
        return win32con.VK_LSHIFT
    if key == 343:  # Left win
        return win32con.VK_LWIN
    if key == 346:  # Right alt
        return win32con.VK_RMENU
    if key == 345:  # Right control
        return win32con.VK_RCONTROL
    if key == 344:  # Right shift
        return win32con.VK_RSHIFT
    if key == 347:  # Right win
        return win32con.VK_RWIN
    if key == 257:  # Enter
        return win32con.VK_RETURN
    if key == 256:  # Escape
        return win32con.VK_ESCAPE
    if key == 259:  # Backspace
        return win32con.VK_BACK
    if key == 261:  # Del
        return win32con.VK_DELETE
    if key == 269:  # End
        return win32con.VK_END
    if key == 268:  # Home
        return win32con.VK_HOME
    if key == 260:  # Insert
        return win32con.VK_INSERT
    if key == 267:  # PgDn
        return win32con.VK_NEXT
    if key == 266:  # PgUp
        return win32con.VK_PRIOR
    if key == 280:  # Caps lock
        return win32con.VK_CAPITAL
    if key == 284:  # Pause
        return win32con.VK_PAUSE
    if key == 281:  # Scroll lock
        return win32con.VK_SCROLL
    if key == 348:  # "Menu"
        return win32con.VK_APPS  # Might be wrong
    if key == 283:  # Print screen
        return win32con.VK_SNAPSHOT
    if key in [161, 162]:  # what even are these "world" keys
        return -1  # Definitely wrong
    return -1
