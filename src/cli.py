#!/usr/bin/env python3

import argparse

from IPFSStreamingVideo.ipfs_streaming_video import IPFSStreamingVideo

parser = argparse.ArgumentParser(description='IPFS Streaming Video')
parser.add_argument('-f', '--input-file', help='path of the input file', required=True)
parser.add_argument('-s', '--segment-format', default='%03d.ts', help='filename format of generated .ts files')
parser.add_argument('-o', '--output-dir', default='output', help='path of the output directory')
parser.add_argument('-m', '--master-filename', default='master.m3u8', help='name of the master m3u8 file')
parser.add_argument('-i', '--ipfs', action='store_true', help='add output files to IPFS and amend m3u8 files')
args = parser.parse_args()

ipfs_streaming_video = IPFSStreamingVideo()

# Convert the input file to HLS chunks (.ts files)
# TODO Determine input quality and select correct renditions.
ipfs_streaming_video.convert_to_hls(
    input_file=args.input_file, segment_format=args.segment_format, output_dir=args.output_dir
)

if args.ipfs:
    # Add the chunks to IPFS.
    ipfs_add_response_ts = ipfs_streaming_video.ipfs_add_dir(directory=args.output_dir, pattern='*.ts')
    # pprint.pprint(ipfs_add_response_ts)

    # Rewrite m3u8 playlists.
    ipfs_streaming_video.rewrite_m3u8_files(ipfs_add_response_ts)

    # Add the rewritten m3u8 playlists to IPFS.
    ipfs_add_response_m3u8 = ipfs_streaming_video.ipfs_add_dir(directory=args.output_dir, pattern='*.m3u8')
    # pprint.pprint(ipfs_add_response_m3u8)

    # Generate master m3u8 playlist.
    ipfs_streaming_video.generate_master_m3u8(
        output_dir=args.output_dir,
        filename=args.master_filename,
        ipfs_hashes=ipfs_add_response_m3u8
    )

    # Add m3u8 master playlists to IPFS.
    ipfs_add_response_master_m3u8 = ipfs_streaming_video.ipfs_add_file(
        file_path=f'{args.output_dir}/{args.master_filename}'
    )

    print(f"Master playlist published to http://127.0.0.1:8080/ipfs/{ipfs_add_response_master_m3u8['Hash']}")
