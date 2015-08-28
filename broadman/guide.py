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


def write_guide(guide, out):
    with open(out, 'w') as file:
        json.dump(guide, file)


def find_servers():
    out_dir = path.POOLDIR
    dirs = next(os.walk(out_dir))[1]
    dirs = [x for x in dirs if os.path.isdir(os.path.join(out_dir, x))]
    dirs.remove('.git')
    dirs.remove('master')
    return [os.path.join(path.POOLDIR, x) for x in dirs]


def sync_guide(syncdef):
    return os.system(syncdef)


def main():
    from . import args
    import conz
    cn = conz.Console()

    parser = args.getparser('Sync backlog to servers', has_debug=True,
                            has_verbose=True)
    parser.add_argument('--dir', help='use this to set dir to something other '
                        'than automatically finding all', dest='srv_dir')
    parser.add_argument('--syncdef', help='a single line shell command for '
                        'syncing guide.json, where {} is the path to the guide'
                        '.json file. default: echo {}', dest='syncdef')

    args = parser.parse_args()

    cn.verbose = args.verbose
    cn.debug = args.debug

    try:
        srv_dir = args.srv_dir or find_servers()
        syncdef = args.syncdef or 'echo {}'
        zb_list, tdir = build_zbs(srv_dir, cn)
        print(len(zb_list))
        guide = build_guide(zb_list)
        shutil.rmtree(tdir)
        out_file = os.path.join(path.POOLDIR, 'guide.json')
        write_guide(guide, out_file)
        cn.pok('built guide')
        syncdef = syncdef.format(out_file)
        resp = sync_guide(syncdef)
        if not resp:
            cn.pok('synced guide')
        else:
            cn.png('syncdef failed')
    except cn.ProgressAbrt:
        cn.png('built guide')


if __name__ == '__main__':
    main()
