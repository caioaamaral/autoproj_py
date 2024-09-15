from pathlib import Path

from autoproj_py.package.definition import PackageDefinition


class PackageRegistry():
    _registry = {}
    
    @classmethod
    def __init__(cls, lookup_paths: list[Path]):        
        for path in lookup_paths:
            for autobuild_path in path.rglob("*.autobuild.py"):
                with open(autobuild_path, "r") as file:
                    exec(file.read(), {})
        
        return cls
            
    @classmethod
    def send(cls, package_name: str, package: PackageDefinition):
        cls._registry[package_name] = package
    
    @classmethod
    def get(cls, package_name: str):
        return cls._registry[package_name]
    
    @classmethod
    def keys(cls):
        return cls._registry.keys()

    @classmethod
    def list(cls):
        return list(cls._registry.keys())



# class PackageRegistry(dict[str, PackageDefinition]):
#     def __init__(self, lookup_paths: list[Path]):
#         super(PackageRegistry, self).__init__()
        
#         for path in lookup_paths:
#             for autobuild_path in path.rglob("*.autobuild.py"):
#                 with open(autobuild_path, "r") as file:
#                     # from autoproj_py.autoproj import package
#                     exec(file.read(), {})
#                     # pass
            
    
#     def send(self, package_name: str, package: PackageDefinition):
#         self[package_name] = package
    
#     def get(self, package_name: str):
#         return self[package_name]
    
#     def list(self):
#         return self.keys()
