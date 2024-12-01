import dearpygui.dearpygui as dpg
import tkinter as tk
from tkinter import filedialog
import os
import json
import subprocess
import psutil
import keyboard
from desmume.controls import keymask, Keys
from desmume.emulator import DeSmuME
import time

# Путь к ndstool.exe
NDSTOOL_PATH = 'ndstool.exe'

# Проверка существования ndstool.exe
if not os.path.exists(NDSTOOL_PATH):
    raise FileNotFoundError(f"ndstool.exe not found at {NDSTOOL_PATH}")

# Функции для работы с ROM
def extract_files_from_rom(rom_file, output_directory):
    try:
        subprocess.run([NDSTOOL_PATH, '-x', rom_file, '-d', output_directory], check=True)
        dpg.show_item("extraction_complete_popup")
    except subprocess.CalledProcessError as e:
        print(f"Error during extraction: {e}")
        dpg.show_item("error_popup")

def pack_files_into_rom(input_directory, output_rom_file):
    try:
        # Проверка наличия файлов в директории
        if not os.listdir(input_directory):
            raise FileNotFoundError(f"No files found in the directory: {input_directory}")

        # Создание BAT-файла для упаковки
        bat_content = f"""
        @echo off
        set rom={output_rom_file}
        set dir={input_directory}
        {NDSTOOL_PATH} -c %rom% -9 %dir%\\arm9.bin -7 %dir%\\arm7.bin -h %dir%\\header.bin -y %dir%\\ytable.bin
        """
        bat_file_path = os.path.join(input_directory, "pack_rom.bat")
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(bat_content)

        # Выполнение BAT-файла
        subprocess.run([bat_file_path], check=True)

        dpg.show_item("packing_complete_popup")
    except subprocess.CalledProcessError as e:
        print(f"Error during packing: {e}")
        dpg.show_item("error_popup")
    except FileNotFoundError as e:
        print(e)
        dpg.show_item("error_popup")

config_file = 'emu_config.json'
default_controls = {
    "A": "x",
    "B": "z",
    "X": "s",
    "Y": "a",
    "L": "q",
    "R": "w",
    "Start": "Return",
    "Select": "shift"
}

def load_controls():
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(default_controls, f, indent=4)
        print(f"Configuration file '{config_file}' created with default settings.")
    with open(config_file, 'r') as f:
        return json.load(f)

def kill_desmume_process():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'pythonw.exe':
            for child in proc.children():
                if child.name() == 'Desmume SDL':
                    child.kill()

def run_emulator(rom_path):
    controls = load_controls()

    emu = DeSmuME()
    emu.open(rom_path)
    window = emu.create_sdl_window()
    emu.input.joy_init()

    target_fps = 60
    frame_time = 1.0 / target_fps

    while not window.has_quit():
        start_time = time.time()
        window.process_input()

        if keyboard.is_pressed(controls["A"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_A))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_A))

        if keyboard.is_pressed(controls["B"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_B))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_B))

        if keyboard.is_pressed(controls["X"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_X))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_X))

        if keyboard.is_pressed(controls["Y"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_Y))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_Y))

        if keyboard.is_pressed(controls["L"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_L))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_L))

        if keyboard.is_pressed(controls["R"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_R))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_R))

        if keyboard.is_pressed(controls["Start"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_START))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_START))

        if keyboard.is_pressed(controls["Select"]):
            emu.input.keypad_add_key(keymask(Keys.KEY_SELECT))
        else:
            emu.input.keypad_rm_key(keymask(Keys.KEY_SELECT))

        emu.cycle()
        window.draw()

        elapsed_time = time.time() - start_time
        sleep_time = frame_time - elapsed_time

        if sleep_time > 0:
            time.sleep(sleep_time)

    emu.close()
    kill_desmume_process()
    dpg.show_item("emulation_complete_popup")

# Функции для выбора файлов и папок
def select_file(sender, app_data, user_data):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("ROM files", "*.nds *.ds")])
    if file_path:
        dpg.set_value(user_data, file_path)

def select_directory(sender, app_data, user_data):
    root = tk.Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory()
    if dir_path:
        dpg.set_value(user_data, dir_path)

def select_save_file(sender, app_data, user_data):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".nds", filetypes=[("ROM files", "*.nds")])
    if file_path:
        dpg.set_value(user_data, file_path)

# Функции для обработки кнопок
def unpack_rom(sender, app_data, user_data):
    rom_path = dpg.get_value("rom_path")
    output_dir = dpg.get_value("output_dir")
    if rom_path and output_dir:
        extract_files_from_rom(rom_path, output_dir)

def pack_rom(sender, app_data, user_data):
    input_dir = dpg.get_value("input_dir")
    output_rom_path = dpg.get_value("output_rom_path")
    if input_dir and output_rom_path:
        pack_files_into_rom(input_dir, output_rom_path)
        if dpg.get_value("run_emulator_checkbox"):
            run_emulator(output_rom_path)

def start_emulator(sender, app_data, user_data):
    rom_path = dpg.get_value("rom_path_emu")
    if rom_path:
        run_emulator(rom_path)

# Создание интерфейса
dpg.create_context()
dpg.create_viewport(title='DS Tools', width=1000, height=1000)

# Создание попапов
with dpg.window(label="Extraction Complete", modal=True, no_close=True,
                 width=300, height=100, show=False,
                 tag="extraction_complete_popup"):
    dpg.add_text("Extraction complete!")
    dpg.add_button(label="OK", callback=lambda: dpg.hide_item("extraction_complete_popup"))

with dpg.window(label="Packing Complete", modal=True,
                 no_close=True,
                 width=300,
                 height=100,
                 show=False,
                 tag="packing_complete_popup"):
    dpg.add_text("Packing complete!")
    dpg.add_button(label="OK", callback=lambda: dpg.hide_item("packing_complete_popup"))

with dpg.window(label="Emulation Complete", modal=True,
                 no_close=True,
                 width=300,
                 height=100,
                 show=False,
                 tag="emulation_complete_popup"):
    dpg.add_text("Emulation complete!")
    dpg.add_button(label="OK", callback=lambda: dpg.hide_item("emulation_complete_popup"))

with dpg.window(label="Error", modal=True,
                 no_close=True,
                 width=300,
                 height=100,
                 show=False,
                 tag="error_popup"):
    dpg.add_text("An error occurred!")
    dpg.add_button(label="OK", callback=lambda: dpg.hide_item("error_popup"))

with dpg.window(label="Main menu", no_close=True):
    dpg.add_button(label="Unpack ROM", callback=lambda: dpg.show_item("unpack_rom_window"))
    dpg.add_button(label="Pack ROM", callback=lambda: dpg.show_item("pack_rom_window"))
    dpg.add_button(label="Emulator", callback=lambda: dpg.show_item("emulator_window"))

with dpg.window(label="Unpack ROM", width=800,
                 height=600,
                 show=False,
                 tag="unpack_rom_window"):

    with dpg.group(horizontal=False):
        dpg.add_text("ROM Path")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="rom_path", width=600)
            dpg.add_button(label="...", callback=select_file,
                           user_data="rom_path")

        dpg.add_text("Output Directory")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="output_dir", width=600)
            dpg.add_button(label="...", callback=select_directory,
                           user_data="output_dir")

        dpg.add_button(label="Unpack", callback=unpack_rom)

with dpg.window(label="Pack ROM", width=800,
                 height=600,
                 show=False,
                 tag="pack_rom_window"):

    with dpg.group(horizontal=False):
        dpg.add_text("Input Directory")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="input_dir", width=600)
            dpg.add_button(label="...", callback=select_directory,
                           user_data="input_dir")

        dpg.add_text("Output ROM Path")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="output_rom_path", width=600)
            dpg.add_button(label="...", callback=select_save_file,
                           user_data="output_rom_path")

        dpg.add_checkbox(label="Run Emulator after packing",
                         tag="run_emulator_checkbox")

        dpg.add_button(label="Pack", callback=pack_rom)

with dpg.window(label="Emulator", width=800,
                 height=600,
                 show=False,
                 tag="emulator_window"):

    with dpg.group(horizontal=False):
        dpg.add_text("ROM Path")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="rom_path_emu", width=600)
            dpg.add_button(label="...", callback=select_file,
                           user_data="rom_path_emu")

        dpg.add_button(label="Start Emulator",
                       callback=start_emulator)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
