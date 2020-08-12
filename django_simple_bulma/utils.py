"""Django Simple Bulma utilities. Ultimately helps ensure DRY code."""

from pathlib import Path
from typing import Generator, List, Union

from django.conf import settings

# If BULMA_SETTINGS has not been declared if no extensions
# have been defined, default to all extensions.
if hasattr(settings, "BULMA_SETTINGS"):
    extensions = settings.BULMA_SETTINGS.get("extensions", "_all")
else:
    extensions = "_all"

simple_bulma_path = Path(__file__).resolve().parent

# (Path, str) pairs describing a relative path in an extension and a glob pattern to search for
sass_files_searchs = (
    (Path("src/sass"), "_all.sass"),
    (Path("src/sass"), "*.sass"),
    (Path("src"), "*.s[ac]ss"),
    (Path("dist"), "*.sass"),
    (Path("dist"), "*.min.css"),
    (Path("dist"), "*.css"),
    (Path(""), "*.s[ac]ss"),
)


def is_enabled(extension: Union[Path, str]) -> bool:
    """Return whether an extension is enabled or not"""
    if isinstance(extension, Path):
        return extensions == "_all" or extension.name in extensions
    return extensions == "_all" or extension in extensions


def get_js_files() -> Generator[str, None, None]:
    """Yield all the js files that are needed for the users selected extensions."""
    # For every extension...
    for ext in (simple_bulma_path / "extensions").iterdir():
        # ...check if it is enabled...
        if is_enabled(ext):
            dist_folder = ext / "dist"

            # ...and add its JS file.
            # This really makes a lot of assumptions about the extension,
            # but so does everything else up until here.
            # Basically, try get a minified version first before settling
            # for whatever might be there.
            js_file = next(dist_folder.rglob("*.min.js"), None) or \
                next(dist_folder.rglob("*.js"), None)
            if js_file:
                yield js_file.relative_to(simple_bulma_path).as_posix()


def get_sass_files(ext: Path) -> List[Path]:
    """Given the path to an extension, find and yield all files that should be imported"""
    for rel_path, glob in sass_files_searchs:
        src_files = list((ext / rel_path).rglob(glob))

        for i, src in enumerate(src_files):
            # Remove suffix from css files, otherwise they wont get compiled, only referenced
            if glob.endswith(".css"):
                src = src.with_suffix("")
            src_files[i] = src.relative_to(simple_bulma_path)

        if src_files:
            return src_files

    # Extension has no stylesheets
    return []
