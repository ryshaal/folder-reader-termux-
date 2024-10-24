import os
from pathlib import Path
from datetime import datetime
import logging
from tqdm import tqdm
import json
from colorama import Fore, Style, init
import argparse
from typing import Dict, List, Optional, Union

# Inisialisasi colorama
init(autoreset=True)


class DirectoryScanner:
    def __init__(self):
        self.total_files = 0
        self.total_folders = 0
        self.setup_logging()

    def setup_logging(self) -> None:
        """Konfigurasi logging dengan format yang lebih informatif"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_directory_input(self) -> Path:
        """Meminta dan memvalidasi input direktori dari pengguna"""
        while True:
            try:
                input_dir = input("Masukkan alamat folder yang ingin dibaca: ").strip()
                base_dir = Path(input_dir).resolve(strict=True)
                if not base_dir.is_dir():
                    raise NotADirectoryError("Path yang dimasukkan bukan direktori")
                return base_dir
            except FileNotFoundError:
                logging.error(
                    f"{Fore.RED}Error: Direktori '{input_dir}' tidak ditemukan.{Style.RESET_ALL}"
                )
            except Exception as e:
                logging.error(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

            retry = input("Apakah ingin mencoba lagi? (y/n): ").lower()
            if retry != "y":
                exit()

    def setup_output_directories(self) -> Dict[str, Path]:
        """Menyiapkan direktori output dengan handling yang lebih baik"""
        use_custom_path = (
            input("Apakah Anda ingin menggunakan lokasi penyimpanan sendiri? (y/n): ")
            .strip()
            .lower()
        )

        try:
            if use_custom_path == "y":
                save_path = Path(input("Masukkan lokasi penyimpanan: ").strip())
            else:
                save_path = Path.cwd()

            output_dirs = {
                "markdown": save_path / "result_md",
                "text": save_path / "result_txt",
                "json": save_path / "result_json",
            }

            # Buat semua direktori yang diperlukan
            for dir_path in output_dirs.values():
                dir_path.mkdir(parents=True, exist_ok=True)

            return output_dirs
        except Exception as e:
            logging.error(
                f"{Fore.RED}Error saat membuat direktori output: {str(e)}{Style.RESET_ALL}"
            )
            exit()

    def get_max_depth(self) -> int:
        """Mendapatkan dan memvalidasi input kedalaman maksimum"""
        while True:
            try:
                depth = input(
                    "Masukkan batas kedalaman direktori yang ingin dibaca (0 = tanpa batas): "
                )
                return int(depth)
            except ValueError:
                logging.error(
                    f"{Fore.RED}Error: Masukkan angka yang valid.{Style.RESET_ALL}"
                )

    def list_directory(
        self,
        dir_path: Path,
        level: int = 0,
        max_depth: int = 0,
        for_markdown: bool = True,
    ) -> str:
        """Membaca dan memformat struktur direktori"""
        content = ""
        indent = "  " * level

        if max_depth == 0 or level < max_depth:
            try:
                items = sorted(
                    dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
                )

                for item in tqdm(
                    items, desc=f"Processing: {dir_path.name}", leave=False
                ):
                    try:
                        if item.is_dir():
                            self.total_folders += 1
                            folder_name = item.name
                            if for_markdown:
                                content += f"{indent}- 📁 **{folder_name}**\n"
                            else:
                                content += f"{indent}- [Folder] {folder_name}\n"
                            content += self.list_directory(
                                item, level + 1, max_depth, for_markdown
                            )
                        else:
                            self.total_files += 1
                            if for_markdown:
                                content += f"{indent}- 📄 {item.name}\n"
                            else:
                                content += f"{indent}- [File] {item.name}\n"
                    except PermissionError:
                        logging.warning(
                            f"{Fore.YELLOW}Warning: Tidak dapat mengakses {item}{Style.RESET_ALL}"
                        )
            except PermissionError:
                logging.warning(
                    f"{Fore.YELLOW}Warning: Tidak dapat mengakses {dir_path}{Style.RESET_ALL}"
                )

        return content

    def get_unique_filename(self, filepath: Path) -> Path:
        """Menghasilkan nama file unik jika sudah ada yang sama"""
        if not filepath.exists():
            return filepath

        i = 1
        while True:
            new_filepath = filepath.with_stem(f"{filepath.stem} ({i})")
            if not new_filepath.exists():
                return new_filepath
            i += 1

    def save_results(
        self,
        base_dir: Path,
        markdown_content: str,
        text_content: str,
        output_dirs: Dict[str, Path],
    ) -> None:
        """Menyimpan hasil ke berbagai format file"""
        folder_name = base_dir.name
        today_date = datetime.now().strftime("%Y-%m-%d")

        # Menyimpan Markdown
        markdown_file = self.get_unique_filename(
            output_dirs["markdown"]
            / f"Directory structure {folder_name} {today_date}.md"
        )
        with markdown_file.open("w", encoding="utf-8") as f:
            f.write(f"# Directory Structure for {folder_name}\n\n")
            f.write(f"📁 **{folder_name}**\n\n")
            f.write(markdown_content)
        logging.info(
            f"SUKSES: {Fore.GREEN}Markdown{Style.RESET_ALL} saved as: {Fore.BLUE}{markdown_file}"
        )

        # Menyimpan Text
        text_file = self.get_unique_filename(
            output_dirs["text"] / f"Directory structure {folder_name} {today_date}.txt"
        )
        with text_file.open("w", encoding="utf-8") as f:
            f.write(f"Directory Structure for {folder_name}\n\n")
            f.write(f"{folder_name}\n\n")
            f.write(text_content)
        logging.info(
            f"SUKSES: {Fore.GREEN}Text file{Style.RESET_ALL} saved as: {Fore.BLUE}{text_file}"
        )

        # Menyimpan JSON
        json_file = self.get_unique_filename(
            output_dirs["json"] / f"Directory structure {folder_name} {today_date}.json"
        )
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "directory": folder_name,
                    "total_files": self.total_files,
                    "total_folders": self.total_folders,
                    "scan_date": today_date,
                    "structure": markdown_content,
                },
                f,
                ensure_ascii=False,
                indent=4,
            )
        logging.info(
            f"SUKSES: {Fore.GREEN}JSON file{Style.RESET_ALL} saved as: {Fore.BLUE}{json_file}"
        )

    def show_statistics(self) -> None:
        """Menampilkan statistik scanning"""
        logging.info(
            f"SUKSES: {Fore.GREEN}Total files{Style.RESET_ALL}: {self.total_files}"
        )
        logging.info(
            f"SUKSES: {Fore.GREEN}Total folders{Style.RESET_ALL}: {self.total_folders}"
        )

    def run(self) -> None:
        """Method utama untuk menjalankan scanner"""
        try:
            base_dir = self.get_directory_input()
            output_dirs = self.setup_output_directories()
            max_depth = self.get_max_depth()

            markdown_content = self.list_directory(
                base_dir, max_depth=max_depth, for_markdown=True
            )
            text_content = self.list_directory(
                base_dir, max_depth=max_depth, for_markdown=False
            )

            self.save_results(base_dir, markdown_content, text_content, output_dirs)
            self.show_statistics()

        except KeyboardInterrupt:
            logging.info(
                f"\n{Fore.YELLOW}Scanning dihentikan oleh pengguna.{Style.RESET_ALL}"
            )
        except Exception as e:
            logging.error(f"{Fore.RED}Error tidak terduga: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    scanner = DirectoryScanner()
    scanner.run()
