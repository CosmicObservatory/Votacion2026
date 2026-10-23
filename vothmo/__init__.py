from vothmo.config import FOLDER_DATA, CENSO_DATA, FOLDER_RAW, ELECCIONES_DATA
import os


if not os.path.exists(FOLDER_DATA):
    os.mkdir(FOLDER_DATA)

if not os.path.exists(FOLDER_RAW):
    os.mkdir(FOLDER_RAW)

if not os.path.exists(CENSO_DATA):
    os.mkdir(CENSO_DATA)

if not os.path.exists(ELECCIONES_DATA):
    os.mkdir(ELECCIONES_DATA)

