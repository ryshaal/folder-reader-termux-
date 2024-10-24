import os
from pathlib import Path
from datetime import datetime
import logging
from tqdm import tqdm
import json
from colorama import Fore, Style

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Meminta input dari pengguna untuk alamat folder yang ingin dibaca
try:
    input_dir = input("Masukkan alamat folder yang ingin dibaca: ").strip()
    base_dir = Path(input_dir).resolve(strict=True)
except FileNotFoundError:
    logging.error(f"{Fore.RED}Error: Direktori '{input_dir}' tidak ditemukan.{Style.RESET_ALL}")
    exit()
except Exception as e:
    logging.error(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    exit()

# Meminta input dari pengguna untuk lokasi penyimpanan file
use_custom_path = input("Apakah Anda ingin menggunakan lokasi penyimpanan sendiri? (y/n): ").strip().lower()

if use_custom_path == 'y':
    try:
        save_path = input("Masukkan lokasi penyimpanan: ").strip()
        result_md_dir = Path(save_path) / "result_md"
        result_txt_dir = Path(save_path) / "result_txt"
        result_json_dir = Path(save_path) / "result_json"
    except Exception as e:
        logging.error(f"{Fore.RED}Error: Lokasi penyimpanan tidak valid.{Style.RESET_ALL}")
        exit()
else:
    result_md_dir = Path("result_md")
    result_txt_dir = Path("result_txt")
    result_json_dir = Path("result_json")

# Membuat direktori jika belum ada
result_md_dir.mkdir(exist_ok=True)
result_txt_dir.mkdir(exist_ok=True)
result_json_dir.mkdir(exist_ok=True)

# Variabel untuk menyimpan statistik
total_files = 0
total_folders = 0

# Meminta pengguna memasukkan batas kedalaman pembacaan direktori
try:
    max_depth = int(input("Masukkan batas kedalaman direktori yang ingin dibaca (0 = tanpa batas): "))
except ValueError:
    logging.error(f"{Fore.RED}Error: Input tidak valid. Harap masukkan angka.{Style.RESET_ALL}")
    exit()

# Fungsi untuk membaca direktori dan subdirektorinya
def list_directory(dir_path, level=0, for_markdown=True):
    global total_files, total_folders
    content = ""
    indent = "  " * level  # Indentasi untuk struktur folder

    if max_depth == 0 or level < max_depth:  # Cek batas kedalaman
        items = list(dir_path.iterdir())  # Ambil list isi direktori
        for item in tqdm(items, desc=f"Processing: {dir_path.name}", leave=True):
            if item.is_dir():
                total_folders += 1
                if for_markdown:
                    content += f"{indent}- 📁 **{item.name}**\n"  # Markdown dengan tebal
                else:
                    content += f"{indent}- [Folder] {item.name}\n"  # Teks biasa tanpa tebal
                content += list_directory(item, level + 1, for_markdown)
            else:
                total_files += 1
                if for_markdown:
                    content += f"{indent}- 📄 {item.name}\n"  # Markdown
                else:
                    content += f"{indent}- [File] {item.name}\n"  # Teks biasa
    return content

# Fungsi untuk menangani duplikasi file
def get_unique_filename(filepath):
    if not filepath.exists():
        return filepath
    # Jika file sudah ada, tambahkan urutan di belakang namanya
    i = 1
    while True:
        new_filepath = filepath.with_stem(f"{filepath.stem} ({i})")
        if not new_filepath.exists():
            return new_filepath
        i += 1

# Cek apakah direktori ada
if base_dir.exists() and base_dir.is_dir():
    # Ambil hasil pembacaan direktori dalam dua format
    markdown_content = list_directory(base_dir, for_markdown=True)  # Untuk Markdown
    text_content = list_directory(base_dir, for_markdown=False)  # Untuk Teks biasa

    # Format nama file dengan tanggal dan nama folder
    folder_name = base_dir.name  # Nama folder yang dibaca
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Menyimpan file Markdown
    markdown_file = result_md_dir / f"Directory structure {folder_name} {today_date}.md"
    markdown_file = get_unique_filename(markdown_file)
    
    with markdown_file.open("w", encoding="utf-8") as f_md:
        f_md.write(f"# Directory Structure for {folder_name}\n\n")
        f_md.write(f"📁 **{folder_name}**\n\n")  # Menambahkan nama folder utama
        f_md.write(markdown_content)

    logging.info(f"SUKSES: {Fore.GREEN}{Style.BRIGHT}Markdown{Style.RESET_ALL} saved as: {Fore.BLUE}{markdown_file}{Style.RESET_ALL}")
    
    # Menyimpan file Teks
    text_file = result_txt_dir / f"Directory structure {folder_name} {today_date}.txt"
    text_file = get_unique_filename(text_file)
    
    with text_file.open("w", encoding="utf-8") as f_txt:
        f_txt.write(f"Directory Structure for {folder_name}\n\n")
        f_txt.write(f"{folder_name}\n\n")  # Menambahkan nama folder utama
        f_txt.write(text_content)

    logging.info(f"SUKSES: {Fore.GREEN}{Style.BRIGHT}Text file{Style.RESET_ALL} saved as: {Fore.BLUE}{text_file}{Style.RESET_ALL}")
    
    # Menyimpan file JSON
    json_file = result_json_dir / f"Directory structure {folder_name} {today_date}.json"
    json_file = get_unique_filename(json_file)
    
    with json_file.open("w", encoding="utf-8") as f_json:
        json.dump({
            "directory": folder_name,
            "structure": markdown_content  # atau text_content, sesuai kebutuhan
        }, f_json, ensure_ascii=False, indent=4)

    logging.info(f"SUKSES: {Fore.GREEN}{Style.BRIGHT}JSON file{Style.RESET_ALL} saved as: {Fore.BLUE}{json_file}{Style.RESET_ALL}")
    
    # Tampilkan statistik
    logging.info(f"SUKSES: {Fore.GREEN}{Style.BRIGHT}Total files{Style.RESET_ALL}: {total_files}")
    logging.info(f"SUKSES: {Fore.GREEN}{Style.BRIGHT}Total folders{Style.RESET_ALL}: {total_folders}")
    
else:
    logging.error(f"{Fore.RED}Error: Direktori {base_dir} tidak ditemukan!{Style.RESET_ALL}")
