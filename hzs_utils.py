import os

class HZSFileHelper:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.path.expanduser('~')

    def hzs_is_pdf(self, path):
        return isinstance(path, str) and path.lower().endswith('.pdf') and os.path.isfile(path)

    def hzs_filename(self, path):
        return os.path.basename(path)

def hzs_format_path(path, max_len=60):
    if not isinstance(path, str):
        return ''
    if len(path) <= max_len:
        return path
    head = path[:int(max_len*0.6)]
    tail = path[-int(max_len*0.4):]
    return f'{head}...{tail}'
