# This files purpose is to walk the entire /pics directory and construct a
# sqlite file that can be used to feed the initial sorter. The created sqlite
# file is simply a single table where each row is the relative path to a .jpg,
# with default values for the other columns.
#
# When given to the ML-Sorter, n-sized-batches of paths will be handed in and 
# each row will be updated with it's reject-or-pass value (0 or -1)
# The purpose at this stage is merely to sort out what pictures from instagram
# are not appropriate to hand in to the face-rater i.e, pictures with no girls
# in it. We make no judgement at this stage as to whether a girl is acceptable
# or not.
#
# The larger idea is to make it so that the ml-sorter can do this sorting stage
# in chunks, and thus can more gracefully recover from errors and not force us
# to run the whole 180k images over again for each crash.

import sqlite3, os, sys

dbloc = "./sortdb.sqlite"
EXTS = [".jpg", ".jpeg", ".gif", ".png"]

def _CheckDbExits():
    isf = os.path.isfile(dbloc)
    return isf

def _SqlGet():
    conn = sqlite3.connect(dbloc)
    cursor = conn.cursor()
    return conn, cursor

def _MakeDb():
    conn, cursor = _SqlGet()
    cursor.close()
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(scriptdir, 'sortdb.sql'), 'r', encoding="utf8") as f:
        t = f.read()
        print(t)
        conn.executescript(t)
    return

def MakeDbIfNotExist():
    print("Checking if DB exists...")
    if not _CheckDbExits():
        print("DB did not exist. Creating.")
        _MakeDb()
        return False
    print("DB existed.")
    return True
    
def _Insert(batch):
    """
    batch: [path-from-cwd]
    """
    conn, cursor = _SqlGet()
    q = "INSERT OR IGNORE INTO pics (path) VALUES (?)"
    cursor.executemany(q, batch)
    conn.commit()
    print("Inserted {0} items".format(len(batch)))
    return

def Prowl(loc="../pics",  exts=EXTS, n = 1000):
    """
    walks every subdirectory of the tree starting at 'loc'
    looking for files that match extensions of 
    [.jpg, .jpeg, .png, .gif]
    matching items are then added to the database a thousad at a time
    """
    n = 1000
    for root, _, fnames in os.walk(loc):
        batch = []
        if fnames: # only dirs with files.
            print("Inserting directory {0}".format(root))
            batch = [(os.path.join(root, x).replace(loc, ""),) for x in fnames if os.path.splitext(x)[1].lower() in exts]
            _Insert(batch)
    return

def main():
    fpath = "./"
    if sys.argv and len(sys.argv) > 1:
        fpath = sys.argv[1]
        if not os.path.isdir(fpath):
            print("Could not find supplied directory: {0}".format(fpath))
            return 1
    MakeDbIfNotExist()
    Prowl(fpath)
    return 0

if __name__ == "__main__":
    sys.exit(main())