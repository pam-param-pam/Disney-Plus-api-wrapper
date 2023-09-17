#!/usr/bin/python3
# coding: utf-8

"""
This module is for I/O.
"""

import multiprocessing
import os
import re
from operator import itemgetter
from pathlib import Path

import requests


def rename_filename(filename):
    """Fix invalid character from title"""

    filename = (
        filename.replace(" ", ".")
        .replace("'", "")
        .replace('"', "")
        .replace(",", "")
        .replace("-", "")
        .replace(":", ".")
        .replace("’", "")
        .replace('"', '')
        .replace("-.", ".")
        .replace(".-.", ".")
    )
    filename = re.sub(" +", ".", filename)
    for _ in range(5):
        filename = re.sub(r"(\.\.)", ".", filename)
    filename = re.sub(r'[/\\:|<>"?*\0-\x1f]|^(AUX|COM[1-9]|CON|LPT[1-9]|NUL|PRN)(?![^.])|^\s|[\s.]$',
                      "", filename[:255], flags=re.IGNORECASE)

    return filename


def download_file(url, output_path, headers=None):
    """Download file from url and show progress"""

    if not headers:
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

    res = requests.get(url, headers=headers, stream=True, timeout=10)
    with open(output_path, 'wb') as file:
        for data in res.iter_content(chunk_size=1024):
            file.write(data)


def download_files(files, headers=None):
    """Multi-processing download files"""
    cpus = multiprocessing.cpu_count()
    max_pool_size = 8
    pool = multiprocessing.Pool(
        cpus if cpus < max_pool_size else max_pool_size)

    lang_paths = []
    for file in sorted(files, key=itemgetter('name')):
        if 'url' in file and 'name' in file and 'path' in file:
            if 'segment' in file and file['segment']:
                extension = Path(file['name']).suffix
                sequence = str(lang_paths.count(file['path'])).zfill(3)
                if file['segment'] == 'comment':
                    filename = os.path.join(file['path'], file['name'].replace(
                        extension, f'-seg_{sequence}_comment{extension}'))
                else:
                    filename = os.path.join(file['path'], file['name'].replace(
                        extension, f'-seg_{sequence}{extension}'))
                lang_paths.append(file['path'])
            else:
                filename = os.path.join(file['path'], file['name'])
            pool.apply_async(download_file, args=(
                file['url'], filename, headers))
    pool.close()
    pool.join()


def download_audio(m3u8_url, output):
    """Download audios from m3u8 url"""

    os.system(
        f'ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto -i "{m3u8_url}" -c copy "{output}" -preset ultrafast -loglevel warning -hide_banner -stats')
