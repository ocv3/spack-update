import os
import shutil
from pathlib import Path

import pexpect

spack_repo_path = "/home/ubuntu/spack_repo/sanger_hgi/packages/"
wsti_dirs = os.listdir(spack_repo_path)
set_packages = set()
c = 0

for pkg in wsti_dirs:
    c+=1
    file_path = Path(f"{spack_repo_path}{pkg}/package.py")

    if os.path.exists(f"/home/ubuntu/spack-packages/repos/spack_repo/builtin/packages/{pkg}"):
        print(f"\tRemoving {pkg}")
        shutil.rmtree(file_path.parent)
    elif os.path.exists(f"/home/ubuntu/spack-packages/repos/spack_repo/builtin/packages/{pkg.replace("-","_")}"):
        print(f"\tRemoving {pkg}")
        shutil.rmtree(file_path.parent)

    print(f"Rename {spack_repo_path}{pkg} -> {spack_repo_path}{pkg.replace("-","_")}")

    os.rename(f"{spack_repo_path}{pkg}", f"{spack_repo_path}{pkg.replace("-","_")}")

    with open(file_path, "r") as f:
        data = f.read()

    new_data = []
    for l in data.splitlines():
        if "-" in l and ("depends_on" in l or "when" in l):
            print(f"{l} -> {l.replace("-", "_")}")
            l = l.replace("-", "_")

        new_data.append(l)

        with open(file_path, "w") as f:
            f.write("\n".join(new_data))

    with open(file_path) as f:
        data = f.read()

    new_data = data.splitlines()
    last_doc = 0
    base_import = "from spack_repo.builtin.build_systems"
    for k, l in enumerate(new_data):
        if "#" in l:
            last_doc = k + 2

        if "(RPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.r import RPackage")
            break

        if "(AutotoolsPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.autotools import AutotoolsPackage")
            break

        if "(Package)" in l:
            new_data.insert(last_doc, f"{base_import}.generic import Package")
            break

        if "(CMakePackage)" in l:
            new_data.insert(last_doc, f"{base_import}.cmake import CMakePackage")
            break

        if "(MakefilePackage)" in l:
            new_data.insert(last_doc, f"{base_import}.makefile import MakefilePackage")
            break

        if "(MesonPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.meson import MesonPackage")
            break

        if "(BundlePackage)" in l:
            new_data.insert(last_doc, f"{base_import}.bundle import BundlePackage")
            break

        if "(PythonPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.python import PythonPackage")
            break

        if "(PerlPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.perl import PerlPackage")
            break

        if "(SConsPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.scons import SConsPackage")
            break

        if "(MavenPackage)" in l:
            new_data.insert(last_doc, f"{base_import}.maven import MavenPackage")
            break

    if new_data[-1] != "":
        new_data.append("")

    new_data = "\n".join(new_data)


    with open(file_path, "w") as f:
        f.write(new_data)

