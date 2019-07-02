# IPFS Streaming Video

Converts an input media to HLS, optionally adding output chunks to IPFS and generating M3U8 playlists containing their IPFS hashes.

### Usage

#### CLI

````bash
src/cli.py --help
````

For example, to convert `examples/input.mp4` to HLS, add the output chunks to IPFS and generate M3U8 playlists containing their IPFS hashes:

```bash
src/cli.py --ipfs --input-file examples/input.mp4
```

#### Module

An example of `IPFSStreamingVideo()` module usage can be seen in `src/cli.py`