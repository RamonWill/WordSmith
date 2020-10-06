from os import walk
from pathlib import Path


class File(object):
    def __init__(self, full_path):
        self.file_path = full_path
        self.name = None
        self.size = None
        self.file_type = None
        self.parent_folder = None
        self._setup()

    def __repr__(self):
        return f"{self.name}"

    def _setup(self):
        print(self.file_path)
        p = Path(self.file_path)
        self.name = p.name
        if p.suffix == "":
            raise FileNotFoundError(
                f"{self.file_path} has to be a file not a folder"
                )

        self.file_type = p.suffix
        self.size = p.stat().st_size  # size displayed in bytes
        self.parent_folder = str(p.parent)


class Folder(object):
    def __init__(self, full_path, include_subfolders=False):
        self.folder_path = full_path
        self.includes_subfolders = include_subfolders
        self.folder_files = ()
        self._extract_files(include_subfolders)

    def __repr__(self):
        return f"{self.folder_path}"

    def _extract_files(self, seek_subfolders=False):
        all_files = []
        for (dirpath, dirnames, filenames) in walk(self.folder_path, topdown=True):
            for filename in filenames:
                file_path = fr"{dirpath}\{filename}"
                print(file_path)
                file = File(file_path)
                all_files.append(file)
            if not seek_subfolders:
                break
        if all_files:
            self.folder_files = tuple(all_files)

    def show_files(self, pretty_print=False):
        print(self)
        if not pretty_print:
            print(self.folder_files)
        else:
            for file in self.folder_files:
                print(f"Name: {file.name}\n  Size: {file.size}")


class AttackTargets(object):
    def __init__(self):
        self.targets = []  # a list of file and folder object

    def add_target(self, target):
        # A target is a tuple in the form ["type", "include_subfolders", "target_path"]
        target_type = target[0]
        include_subfolders = target[1]
        target_path = target[2]
        if target_type == "File":
            self._add_target_file(target_path=target_path)
        else:
            self._add_target_folder(target_path=target_path,
                                    include_subfolders=include_subfolders)

    def _add_target_file(self, target_path):
        raw_target = fr"{target_path}"
        t = File(raw_target)
        self.targets.append(t)

    def _add_target_folder(self, target_path, include_subfolders=False):
        raw_target = fr"{target_path}"
        t = Folder(raw_target, include_subfolders)
        self.targets.append(t)

    def get_targets(self):
        return self.targets

    def show_targets(self, pretty_print=False):
        if not self.targets:
            print("There are no targets")
        for count, item in enumerate(self.targets, 1):
            if isinstance(item, File):
                print(f"Target {count}.\n{item}")
            else:
                print(f"Target {count}.\n")
                item.show_files(pretty_print)



## Password file location
#https://www.kaggle.com/wjburns/common-password-list-rockyoutxt
