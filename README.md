# Acheron

A small, living look at your system. Acheron turns CPU, memory, and network activity into a quiet terminal ecosystem, with no setup beyond a one-line install.

## Install

**Linux and macOS**

```bash
curl -fsSL https://raw.githubusercontent.com/ak495867/Acheron/master/install.sh | bash
```

**Windows PowerShell**

```powershell
irm https://raw.githubusercontent.com/ak495867/Acheron/master/install.ps1 | iex
```

Python 3.9 or newer is required. The installer creates a private virtual environment for Acheron and installs its small system-metrics dependency there.

## Use

```text
acheron
```

Press `q` to leave. `Ctrl+C` also returns you to your shell. For a single reading, use `acheron --once`.

## What it watches

- CPU activity
- Memory use
- Live network traffic in both directions

Acheron samples locally and sends no data anywhere.

## Update or remove

Run the install command again to update. On Linux and macOS, remove `~/.local/share/acheron` and `~/.local/bin/acheron`. On Windows, remove `%LOCALAPPDATA%\Acheron` and remove its `bin` folder from your user `Path` if you no longer want the command.

## License

MIT, copyright (c) 2026 ak495867.
