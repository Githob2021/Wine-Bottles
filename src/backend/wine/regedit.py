from typing import NewType

from bottles.backend.logger import Logger # pyright: reportMissingImports=false
from bottles.backend.wine.wineprogram import WineProgram

logging = Logger()

# Define custom types for better understanding of the code
BottleConfig = NewType('BottleConfig', dict)


class Regedit(WineProgram):
    program = "WINE Registry Editor"
    command = "regedit"
