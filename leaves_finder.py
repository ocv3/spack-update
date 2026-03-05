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
            return None

        if key_to_search in buffer:
            if c == "f":
                continue
            buffer = ""
            in_dep = True
            continue

        if c in [" ", "+", "@", "'", '"', "~", ",", "%", "{"] and in_dep:
            if buffer == '':
                print(f"{origin}:-> {buffer} from {line}")

                if origin=="dd4hep":
                    return ["boost", "root"], []

                if origin == "py-tensorflow":
                    return [
                        "hip",
                        "rocrand",
                        "rocblas",
                        "rocfft",
                        "hipfft",
                        "rccl",
                        "hipsparse",
                        "rocprim",
                        "hsa-rocr-dev",
                        "rocminfo",
                        "hipsolver",
                        "hiprand",
                        "rocsolver",
                        "hipsolver",
                        "hipblas",
                        "hipcub",
                        "rocm-core",
                        "roctracer-dev",
                        "miopen-hip",
                    ], ["+rocm"]

                if origin == "fairroot":
                    return ["root", "fairmq"], []

                if origin == "seissol":
                    return ["openmpi", "mpich", "mvapich-plus"], []

                if origin == "py-jaxlib":
                    return [
                        "comgr",
                        "hip",
                        "hipblas",
                        "hipblaslt",
                        "hipcub",
                        "hipfft",
                        "hiprand",
                        "hipsolver",
                        "hipsparse",
                        "hsa-rocr-dev",
                        "miopen-hip",
                        "rccl",
                        "rocblas",
                        "rocfft",
                        "rocminfo",
                        "rocprim",
                        "rocrand",
                        "rocsolver",
                        "rocsparse",
                        "roctracer-dev",
                        "rocm-core",
                    ], []

                if origin == "axom":
                    return ["adiak", "caliper"], ["+profiling"]

                if origin == "py-onnxruntime":
                    return [
                        "hsa-rocr-dev",
                        "hip",
                        "hiprand",
                        "hipsparse",
                        "hipfft",
                        "hipcub",
                        "hipblas",
                        "llvm-amdgpu",
                        "miopen-hip",
                        "migraphx",
                        "rocblas",
                        "rccl",
                        "rocprim",
                        "rocminfo",
                        "rocm-core",
                        "rocm-cmake",
                        "roctracer-dev",
                        "rocthrust",
                        "rocrand",
                        "rocsparse",
                    ], ["+rocm"]

                if origin == "tandem":
                    return ["openmpi", "mpich", "mvapich-plus"], []

                if origin == "celeritas":
                    return ["geant4", "root", "vecgeom", "covfie", "vecgeom", "covfie", "vecgeom"], []


            if buffer == 'ang':
                return "java", []
            if buffer == 'oost.with_default_variants':
                return "boost", []
            if buffer == 'py-':
                return ["py-pyqt5", "py-pyqt4", "py-pyside2"], []
            return buffer, []

        buffer += c
    return None, []


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
            d, variants = parse_line(l, "depends_on(", name)

            for v in variants:
                self.variant.add(v)
            if isinstance(d, str):
                self.dependencies.add(d)
                continue
            elif isinstance(d, list):
                for dep in d:
                    self.dependencies.add(dep)

            d = parse_line(l, "provides(", name)
            for v in variants:
                self.variant.add(v)
            if d:
                self.provides.add(d)
                if d not in packages:
                    packages[d] = [self]
                else:
                    packages[d].append(self)
                continue

    def __str__(self):
        return f"{self.name}: {self.path}\n\tProvides: {self.provides}\n\tDepends on: {self.dependencies}"

    @property
    def package_file_path(self):
        return os.path.join(self.path, "package.py")


for pkg in wsti_dirs:
    p_name = pkg.replace("_","-")
    p = Package(p_name, wtsi_repo_path + pkg)
    packages[p_name] = [p]

for pkg in spack_dirs:
    if "__init__" in pkg:
        continue

    p_name = pkg.replace("_","-")
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
