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


def load_meta(cdir):
    """ Takes a CID path; returns metadata as a dict """
    meta_path = path.infopath(cdir)
    meta = open(meta_path, 'r').read()
    return json.loads(meta)


def get_size(cdir):
    """ Takes a cid; returns uncompressed total size """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(cdir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def get_compressed_size(cid, tdir, cdir):
    """ Takes a cid, temporary dir, and cdir; returns compressed total size """
    zname = cid + '.zip'
    zpath = os.path.join(tdir, zname)
    zips.pack(zpath, cdir)
    return os.path.getsize(zpath)


def get_info(cid, tdir):
    """ Takes a cid; returns compressed/uncompressed size and title """
    cdir = next(path.find_contentdirs(cid)) # find_contentdirs returns a generator
    meta = load_meta(cdir)
    title = meta['title']
    size = get_size(cdir)
    compressed = get_compressed_size(cid, tdir, cdir)
    return {'title': title, 'compressed_size': compressed, 'uncompressed_size': size}


def write_guide(guide, out):
    """ Takes a dict and a filepath; writes the dict to the file """
    with open(out, 'w') as file:
        json.dump(guide, file)


def find_servers():
    """ Finds all servers in the pooldir; returns a list of directories, except .git and master """
    out_dir = path.POOLDIR
    dirs = next(os.walk(out_dir))[1]
    dirs = [x for x in dirs if os.path.isdir(os.path.join(out_dir, x))]
    dirs.remove('.git')
    dirs.remove('master')
    return [os.path.join(path.POOLDIR, x) for x in dirs]


def build_list(servers):
    """ Takes a list of servers; returns a list of cids """
    if type(servers) == str:
        return os.listdir(servers)
    zipball_list = []
    for server in servers:
        zipball_list.extend(os.listdir(server))
    return zipball_list


def build_guide(cid_list):
    """ Builds a guide dict from a list of cids """
    compiled = {}
    tdir = tempfile.mkdtemp()
    for cid in cid_list:
        compiled[cid] = get_info(cid, tdir)
    shutil.rmtree(tdir)
    return(compiled)


def main():
    from . import args
    import conz
    cn = conz.Console()

    parser = args.getparser('Sync backlog to servers', has_debug=True,
                            has_verbose=True)
    parser.add_argument('--server', '-s', help='use this to set the server to '
                        'something other than automatically finding all',
                        dest='servers')
    parser.add_argument('--print', '-p', help='print to stdout instead of '
                        'writing to a file', action='store_true', dest='print')

    args = parser.parse_args()

    cn.verbose = args.verbose
    cn.debug = args.debug

    servers = args.servers or find_servers()
    cid_list = build_list(servers)
    cn.pok('zipballs found: {}'.format(len(cid_list)))
    guide = build_guide(cid_list)
    cn.pok('built guide')
    p = args.print or False
    if not p:
        out_file = 'guide.json'
        write_guide(guide, out_file)
        cn.pok('wrote guide')
    else:
        print(guide)


if __name__ == '__main__':
    main()
