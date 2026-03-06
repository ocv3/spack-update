import os

wtsi_repo_path = "/home/ubuntu/spack_repo/sanger_hgi/packages/"
wsti_dirs = os.listdir(wtsi_repo_path)

spack_repo_path = "/home/ubuntu/spack-packages/repos/spack_repo/builtin/packages/"
spack_dirs = os.listdir(spack_repo_path)

packages = dict()


def parse_line(line, key_to_search, origin):
    buffer = ""
    in_dep = False

    for c in line:
        if c == "#":
            return []

        if key_to_search in buffer:
            if c == "f":
                continue
            buffer = ""
            in_dep = True
            continue

        if c in [" ", "+", "@", "'", '"', "~", ",", "%", "{"] and in_dep:
            if buffer == 'ang':
                buffer = "java"
            if buffer == 'oost.with_default_variants':
                buffer = "boost"

            if origin[0] == 'er' and buffer == "ep":
                return ["kvtree", "rankstr", "redset", "shuffile"]

            if origin[0] == "chapel" and buffer == "ep":
                return []

            if origin[0] == "gaudi" and buffer == "v[0]":
                return ["catch2", "py-nose", "py-pytest"]

            if origin[0] == "scr" and buffer == "omp":
                return ["axl", "dtcmp", "er", "kvtree", "rankstr", "redset", "shuffile", "spath"]

            if origin[0] in ["py-qtpy", "py-pyqtgraph"] and buffer == "py-":
                return ["py-pyqt5", "py-pyqt4", "py-pyside2"]

            if origin[0] == "spiral-software" and buffer == "spiral-package-":
                return [f"spiral-package-{_p}" for _p in ["fftx", "simt", "mpi", "jit", "hcol"]]

            if origin[0] == "cabana" and buffer == "kk_spec":
                return []

            if origin[0] == "geant4-data" and buffer == "d":
                return ['g4tendl', 'g4radioactivedecay', 'g4channeling', 'g4incl', 'g4particlexs', 'g4pii',
                        'g4photonevaporation', 'g4ndl', 'g4abla', 'g4realsurface', 'g4saiddata', 'g4neutronxs',
                        'g4emlow', 'g4ensdfstate']

            if origin[0] == "cutensor" and buffer == "uda_req":
                return ["cuda"]

            if origin[0] == "dealii" and buffer == "rilinos_spec":
                return ["trilinos"]

            if origin[0] == "kokkos-kernels" and buffer == "packname":
                return []

            if origin[0] == "kokkos" and buffer == "pl":
                return []

            if origin[0] == "dav-sdk" and buffer == "pec":
                return ["adios2", "hdf5", "parallel-netcdf", "ascent", "diy", "paraview", "libcatalyst", "visit",
                        "vtk-m", "zfp"]

            if origin[0] == "ecp-data-vis-sdk" and buffer == "pec":
                return ["adios2", "darshan-runtime", "darshan-util", "faodel", "hdf5", "parallel-netcdf", "unifyfs",
                        "veloc", "sensei", "ascent", "paraview", "libcatalyst", "visit", "vtk-m", "sz", "zfp"]

            if origin[0] == "xsdk" and buffer in ["pec", "args_new"]:
                return ["hypre", "mfem", "superlu-dist", "trilinos", "datatransferkit", "petsc", "dealii", "pflotran",
                        "alquimia", "sundials", "plasma", "magma", "amrex", "slepc", "omega-h", "strumpack", "pumi",
                        "tasmanian", "arborx", "phist", "ginkgo", "py-libensemble", "py-petsc4py", "precice",
                        "butterflypack", "heffte", "slate", "exago", "hiop"]

            return [buffer]

        buffer += c
    return []


class Package:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.dependencies = set()
        self.provides = set()
        self.variant = set()

        with open(self.package_file_path, "r") as f:
            recipe_lines = f.read().splitlines()

        for l in recipe_lines:
            for dep in parse_line(l, "depends_on(", (name, self.package_file_path)):
                self.dependencies.add(dep)

            for prv in parse_line(l, "provides(", (name, self.package_file_path)):
                if prv not in packages:
                    packages[prv] = [self]
                else:
                    packages[prv].append(self)

    def __str__(self):
        return f"{self.name}: {self.path}\n\tProvides: {self.provides}\n\tDepends on: {self.dependencies}"

    @property
    def package_file_path(self):
        return os.path.join(self.path, "package.py")


for pkg in wsti_dirs:
    p_name = pkg.replace("_", "-")
    p = Package(p_name, wtsi_repo_path + pkg)
    packages[p_name] = [p]

for pkg in spack_dirs:
    if "__init__" in pkg:
        continue

    p_name = pkg.replace("_", "-")
    p = Package(p_name, spack_repo_path + pkg)
    packages[p_name] = [p]


def get_deps(name):
    full_dep = set()
    missing_deps = set()

    def _get_deps(_name):
        if _name in full_dep:
            return

        full_dep.add(_name)
        try:
            pypack = packages[_name][0]
        except KeyError as e:
            missing_deps.add(_name)
            return

        for dep in pypack.dependencies:
            _get_deps(dep)

    _get_deps(name)
    return full_dep, missing_deps


all_pkgs = set(packages.keys())
leaves = []
missing = set()

for k in packages.keys():
    d, m = get_deps(k)
    missing = missing.union(m)
    all_pkgs = all_pkgs - d
    leaves.append(k)
    if len(all_pkgs) == 0:
        print("DONE")
        print(leaves)
        print(missing)
        exit()
