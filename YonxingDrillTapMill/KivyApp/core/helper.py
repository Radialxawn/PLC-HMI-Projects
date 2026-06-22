from pathlib import Path

class Helper(object):
    @staticmethod
    def path_get(_folder_):
        folder = f'Desktop/{_folder_}'
        rootpath = Path.home() / folder
        if not rootpath.exists():
            rootpath.mkdir(parents=True, exist_ok=True)
        return rootpath