set -euo pipefail

repo="https://raw.githubusercontent.com/ak495867/Acheron"
branch="${ACHERON_BRANCH:-master}"
base="${XDG_DATA_HOME:-$HOME/.local/share}/acheron"
bin="$HOME/.local/bin"

if ! command -v curl >/dev/null 2>&1; then
    printf '%s\n' 'Acheron needs curl. Install curl and run the installer again.' >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Acheron needs Python 3.9 or newer. Install Python and run the installer again.' >&2
    exit 1
fi

python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' || {
    printf '%s\n' 'Acheron needs Python 3.9 or newer.' >&2
    exit 1
}

mkdir -p "$base/src" "$bin"
curl -fsSL "$repo/$branch/pyproject.toml" -o "$base/pyproject.toml"
curl -fsSL "$repo/$branch/README.md" -o "$base/README.md"
curl -fsSL "$repo/$branch/LICENSE" -o "$base/LICENSE"
curl -fsSL "$repo/$branch/src/acheron.py" -o "$base/src/acheron.py"
python3 -m venv "$base/venv"
"$base/venv/bin/python" -m pip install --upgrade --force-reinstall --disable-pip-version-check "$base"
ln -sfn "$base/venv/bin/acheron" "$bin/acheron"
printf '\nAcheron is ready. Run: acheron\n'
case ":$PATH:" in
    *":$bin:"*) ;;
    *) printf 'If the command is not found, add %s to your PATH.\n' "$bin" ;;
esac
