# IPFS Streaming Video

Converts an input video file to HLS at multiple qualities, optionally adding output chunks and amended M3U8 playlists to IPFS.

## Usage

### Command-Line Interface

````bash
python3 src/cli.py --help
````

For example:

```bash
python3 src/cli.py --ipfs --input-file examples/input.mp4
```

### Python Module

An example of `IPFSStreamingVideo()` Python module usage can be seen in `src/cli.py`

### Web Player

An example HLS-capable web player can be found at `examples/player.html`, which can also be added to IPFS! Just change M3U8 playlist hash in `player.html` to the one returned by the CLI.

## Contributing

All contributions are welcome. Just open a Pull Request or Issue.
