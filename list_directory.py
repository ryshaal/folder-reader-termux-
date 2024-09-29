import os
from pathlib import Path
from datetime import datetime
import shutil

# Meminta input dari pengguna untuk alamat folder yang ingin dibaca
input_dir = input("Masukkan alamat folder yang ingin dibaca: ").strip()

# Lokasi direktori yang ingin dibaca
base_dir = Path(input_dir)

# Lokasi folder result untuk menyimpan file Markdown dan Teks
result_md_dir = Path("result_md")
result_txt_dir = Path("result_txt")
result_md_dir.mkdir(exist_ok=True)  # Membuat folder result_md jika belum ada
result_txt_dir.mkdir(exist_ok=True)  # Membuat folder result_txt jika belum ada

# Fungsi untuk membaca direktori dan subdirektorinya
def list_directory(dir_path, level=0, for_markdown=True):
    content = ""
    indent = "  " * level  # Indentasi untuk struktur folder
    
    # Loop melalui isi direktori
    for item in dir_path.iterdir():
        if item.is_dir():
            # Format folder berbeda antara Markdown dan teks biasa
            if for_markdown:
                content += f"{indent}- 📁 **{item.name}**\n"  # Markdown dengan tebal
            else:
                content += f"{indent}- [Folder] {item.name}\n"  # Teks biasa tanpa tebal
            # Rekursif untuk membaca isi subfolder
            content += list_directory(item, level + 1, for_markdown)
        else:
            # Format file berbeda antara Markdown dan teks biasa
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

    print(f"Markdown saved as: {markdown_file}")
    
    # Menyimpan file Teks
    text_file = result_txt_dir / f"Directory structure {folder_name} {today_date}.txt"
    text_file = get_unique_filename(text_file)
    
    with text_file.open("w", encoding="utf-8") as f_txt:
        f_txt.write(f"Directory Structure for {folder_name}\n\n")
        f_txt.write(f"{folder_name}\n\n")  # Menambahkan nama folder utama
        f_txt.write(text_content)

    print(f"Text file saved as: {text_file}")
    
else:
    print(f"Directory {base_dir} does not exist!")
