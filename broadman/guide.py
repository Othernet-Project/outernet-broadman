import os
import json
import shutil
import tempfile
from . import path
from . import zips

try:
    FILE_ERRORS = (IOError, OSError, FileNotFoundError)
except NameError:
    FILE_ERRORS = (IOError, OSError)


def load_meta(cid_path):
    meta_path = path.infopath(cid_path)
    meta = open(meta_path, 'r').read()
    return json.loads(meta)


def get_title(cid_path):
    meta = load_meta(cid_path)
    return meta['title']


def get_size(cid_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(cid_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def process_zipball(zb):
    compressed = os.path.getsize(zb)
    cid_path = next(path.find_contentdirs(zb)) # find_contentdirs returns a generator
    title = get_title(cid_path)
    size = get_size(cid_path)
    return {'compressed': compressed, 'title': title, 'size': size}


def build_guide(zb_list):
    compiled = {}
    for zb in zb_list:
        md5, ext = os.path.basename(zb).split('.')
        info = process_zipball(zb)
        compiled[md5] = info
    return(compiled)


def build_zbs(srv_dir, cn):
    zb_list = []
    for srv in srv_dir:
        for dirpath, dirnames, filenames in os.walk(srv):
            zb_list.extend(dirnames)

    tdir = tempfile.mkdtemp()
    finished = []

    for zb in zb_list:
        cid = path.cid(zb)
        cdir = path.contentdir(cid)
        with cn.progress('Packing zip file', excs=FILE_ERRORS + (RuntimeError,)):
            zname = cid + '.zip'
            zpath = os.path.join(tdir, zname)
            zips.pack(zpath, cdir)
        finished.append(zpath)
    return finished, tdir


def write_guide(guide):
    print(guide)
    with open('guide.json', 'w') as file:
        json.dump(guide, file)


def find_servers():
    dirs = next(os.walk(path.POOLDIR))[1]
    dirs.remove('.git')
    dirs.remove('master')
    return [os.path.join(path.POOLDIR, x) for x in dirs]


def main():
    from . import args
    import conz
    cn = conz.Console()

    parser = args.getparser('Sync backlog to servers', has_debug=True,
                            has_verbose=True)
    parser.add_argument('--dir', help='use this to set dir to something other '
                        'than automatically finding all', dest='srv_dir')
    args = parser.parse_args()

    cn.verbose = args.verbose
    cn.debug = args.debug

    def fail(msg):
        cn.perr(msg)
        cn.png('built guide')
        cn.quit(1)

    try:
        srv_dir = args.srv_dir or find_servers()
        zb_list, tdir = build_zbs(srv_dir, cn)
        guide = build_guide(zb_list)
        shutil.rmtree(tdir)
        write_guide(guide)
        cn.pok('built guide')
    except cn.ProgressAbrt:
        cn.png('built guide')
    except RuntimeError:
        cn.pok('no backlog', ok='OK')


if __name__ == '__main__':
    main()
