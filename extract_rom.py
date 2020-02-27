import os
import sys
import zipfile
import tempfile
from sdat2img import sdat2img

path = os.getcwd()
print(f'Current working directory is {path}.')
print()

original_package = os.path.abspath(str(sys.argv[1]))
print(f'File to extract: {original_package}')
print()

def main():
    global path, original_package, out
    with tempfile.TemporaryDirectory() as out, zipfile.ZipFile(original_package, 'r') as package:
        print(f'Out folder: {out}')
        print()
        package.extractall(out)
        if "system.new.dat.br" in os.listdir(out):
            print("Decompressing system.new.dat.br")
            print()
            os.system(f'brotli -d {out}/system.new.dat.br -o {out}/system.new.dat')
        if "system.new.dat" in os.listdir(out):
            print("Decompressing system.new.dat")
            print()
            with suppress_stdout():
                sdat2img.main(f'{out}/system.transfer.list', f'{out}/system.new.dat', f'{out}/system.img')

            os.listdir(out)

        if "system.img" in os.listdir(out):
            print("Decompressing sparse image")
            simg = os.system(f'simg2img {out}/system.img {out}/raw.system.img')
            if int(simg) == 0:
                system_img = "raw.system.img"
            else:
                system_img = "system.img"
                print("system.img is not a sparse image, proceeding.")

            try:
                os.mkdir(f'{path}/system')
            except FileExistsError:
                os.system(f'sudo umount {path}/system')
                os.rmdir(f'{path}/system')
                os.mkdir(f'{path}/system')

            os.system(f'sudo mount -t ext4 -o loop {out}/{system_img} {path}/system')
            print("done")


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
