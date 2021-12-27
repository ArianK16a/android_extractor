import os
import pathlib
import shutil
import sys
import tempfile
import zipfile
from utils.sdat2img import sdat2img
from utils.extract_android_ota_payload import extract_android_ota_payload

### start http://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
from contextlib import contextmanager

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
### end http://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/

def extract(partitions):
    if len(sys.argv) == 1:
        print("Usage: python3 extract_rom.py path/to/rom.zip")
        exit(1)

    path = os.getcwd()
    original_package = os.path.abspath(str(sys.argv[1]))
    sparse = True

    with tempfile.TemporaryDirectory() as out, zipfile.ZipFile(original_package, 'r') as package:
        print(f'Unpacking {original_package} temporary.')
        print()
        package.extractall(out)
        for i in pathlib.Path(out).rglob('*.zip'):
            print(f'Unpacking {i} temporary.')
            zipfile.ZipFile(i).extractall(out)
        if "payload.bin" in os.listdir(out):
            extract_android_ota_payload.main(f'{out}/payload.bin', f'{out}')
            sparse = False
        for partition in partitions:
            if partition in os.listdir(path):
                shutil.rmtree(f'{path}/{partition}')

            if partition == "boot":
                if "boot.img" in os.listdir(out):
                    print("unpacking boot.img")
                    print()
                    os.system(f'{os.path.dirname(os.path.realpath(__file__))}/utils/split_boot {out}/{partition}.img')
                else:
                    print(f'Can not get {partition}.img out of {original_package}')
                    print()
                return
            if f'{partition}.new.dat.br' in os.listdir(out):
                print(f'Decompressing {partition}.new.dat.br')
                print()
                os.system(f'brotli -d {out}/{partition}.new.dat.br -o {out}/{partition}.new.dat')

            if f'{partition}.new.dat' in os.listdir(out):
                print(f'Decompressing {partition}.new.dat')
                print()
                with suppress_stdout():
                    sdat2img.main(f'{out}/{partition}.transfer.list', f'{out}/{partition}.new.dat', f'{out}/{partition}.img')

                sparse = False

            if f'{partition}.img' in os.listdir(out):
                img = f'{partition}.img'
                if sparse:
                    print(f'Decompressing sparse image {partition}.img')
                    print()
                    simg = os.system(f'simg2img {out}/{partition}.img {out}/raw.{partition}.img')
                    if int(simg) == 0:
                        img = f'raw.{partition}.img'

                os.mkdir(f'{path}/{partition}')
                os.system(f'7z x {out}/{img} -o{path}/{partition}')
                print(f'Extracted {partition} to {path}/{partition}.')
                print()
            else:
                print(f'Can not get {partition}.img out of {original_package}')
                print()



partitions = ["system", "vendor", "boot"]
extract(partitions)