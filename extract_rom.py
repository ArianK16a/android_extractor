import os
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
    path = os.getcwd()
    original_package = os.path.abspath(str(sys.argv[1]))
    sparse = True

    with tempfile.TemporaryDirectory() as out, zipfile.ZipFile(original_package, 'r') as package:
        print(f'Unpacking {original_package} temporary.')
        print()
        package.extractall(out)
        if "payload.bin" in os.listdir(out):
            extract_android_ota_payload.main(f'{out}/payload.bin', f'{out}')
            sparse = False
        for partition in partitions:
            if partition == "boot":
                print("boot.img, starting now!")
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

                try:
                    os.mkdir(f'{path}/{partition}')
                except FileExistsError:
                    os.system(f'sudo umount {path}/{partition}')
                    os.rmdir(f'{path}/{partition}')
                    os.mkdir(f'{path}/{partition}')

                os.system(f'sudo mount -t ext4 -o loop {out}/{img} {path}/{partition}')
                print(f'Mounted {partition} as {path}/{partition}.')
                print()
            else:
                if partition in os.listdir(path):
                    os.system(f'sudo umount {path}/{partition}')
                    os.rmdir(f'{path}/{partition}')

                print(f'Can not get {partition}.img out of {original_package}')
                print()


partitions = ["system", "vendor", "boot"]
extract(partitions)