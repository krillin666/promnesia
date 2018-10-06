from ..common import get_logger, get_tmpdir

import os.path
import os

# https://linux-and-mac-hacks.blogspot.co.uk/2013/04/use-grep-and-regular-expressions-to.html
_URL_REGEX = r'\b(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|]'

# -n to output line numbers so we could restore context
# -I to ignore binaries
_GREP_CMD = r"""grep --color=never -Eo -I {grep_args} --exclude="*.html~" --exclude="*.html" --exclude-dir=".git" '{regex}' {path}"""


def _extract_from_dir(path: str) -> str:
    return _GREP_CMD.format(
        grep_args="-r -n",
        regex=_URL_REGEX,
        path=path,
    )

def _extract_from_file(path: str) -> str:
    return _GREP_CMD.format(
        grep_args="-n",
        regex=_URL_REGEX,
        path=f"'{path}' /dev/null", # dev null to trick into displaying filename
    )


def extract_from_path(path: str) -> str:
    tdir = get_tmpdir()

    logger = get_logger()
    if os.path.isdir(path): # TODO handle archives here???
        return _extract_from_dir(path)
    else:
        if any(path.endswith(ex) for ex in (
                '.xz',
                '.bz2',
                '.gz',
                '.zip',
        )):
            logger.info(f"Extracting from compressed file {path}")
            import lzma
            from tempfile import NamedTemporaryFile
            # TODO hopefully, no collisions
            fname = os.path.join(tdir.name, os.path.basename(path))
            with open(fname, 'wb') as fo:
                with lzma.open(path, 'r') as cf:
                    fo.write(cf.read())
                return _extract_from_file(fname)
        else:
            return _extract_from_file(path)