import os
import sys
import zipfile
import tempfile
from sdat2img import sdat2img

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

path = os.getcwd()
print(f'Current working directory is {path}.')
print()

original_package = os.path.abspath(str(sys.argv[1]))
print(f'File to extract: {original_package}')
print()


def extract_partition(partition):
    global path, original_package, out
    with tempfile.TemporaryDirectory() as out, zipfile.ZipFile(original_package, 'r') as package:
        print(f'Out folder: {out}')
        print()
        package.extractall(out)
        if f'{partition}.new.dat.br' in os.listdir(out):
            print(f'Decompressing {partition}.new.dat.br')
            print()
            os.system(f'brotli -d {out}/{partition}.new.dat.br -o {out}/{partition}.new.dat')
        if f'{partition}.new.dat' in os.listdir(out):
            print(f'Decompressing {partition}.new.dat')
            print()
            with suppress_stdout():
                sdat2img.main(f'{out}/{partition}.transfer.list', f'{out}/{partition}.new.dat', f'{out}/{partition}.img')

            os.listdir(out)

        if f'{partition}.img' in os.listdir(out):
            print("Decompressing sparse image")
            simg = os.system(f'simg2img {out}/{partition}.img {out}/raw.{partition}.img')
            if int(simg) == 0:
                img = f'raw.{partition}.img'
            else:
                img = f'{partition}.img'
                print(f'{partition}.img is not a sparse image, proceeding.')

            try:
                os.mkdir(f'{path}/{partition}')
            except FileExistsError:
                os.system(f'sudo umount {path}/{partition}')
                os.rmdir(f'{path}/{partition}')
                os.mkdir(f'{path}/{partition}')

            os.system(f'sudo mount -t ext4 -o loop {out}/{img} {path}/{partition}')
            print(f'Mounted {partition}.')
        else:
            print(f'Can not get {partition}.img out of {original_package}')


extract_partition("system")