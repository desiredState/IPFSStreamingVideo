#!/usr/bin/env python3

import argparse
import fileinput
import os

import ffmpeg
import ipfshttpclient


class IPFSStreamingVideo(object):
    def __init__(self):
        self.renditions = [
            # {'name': '240p', 'resolution': '426x240', 'bitrate': '400k', 'audiorate': '64k'},
            # {'name': '360p', 'resolution': '640x360', 'bitrate': '700k', 'audiorate': '96k'},
            # {'name': '480p', 'resolution': '854x480', 'bitrate': '1250k', 'audiorate': '128k'},
            {'name': 'HD 720p', 'resolution': '1280x720', 'bitrate': '2500k', 'audiorate': '128k'},
            # {'name': 'HD 720p 60fps', 'resolution': '1280x720', 'bitrate': '3500k', 'audiorate': '128k'},
            {'name': 'Full HD 1080p', 'resolution': '1920x1080', 'bitrate': '4500k', 'audiorate': '192k'},
            # {'name': 'Full HD 1080p 60fps', 'resolution': '1920x1080', 'bitrate': '5800k', 'audiorate': '192k'},
            # {'name': '4k', 'resolution': '3840x2160', 'bitrate': '14000k', 'audiorate': '192k'},
            # {'name': '4k 60fps', 'resolution': '3840x2160', 'bitrate': '23000k', 'audiorate': '192k'}
        ]

    def convert_to_hls(self, input_file, segment_format='%03d.ts', output_dir='output'):
        ffmpeg_input_stream = ffmpeg.input(input_file)
        ffmpeg_output_streams = []

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for rendition in self.renditions:
            ffmpeg_params = {
                'vf': "scale=w={}:h={}:force_original_aspect_ratio=decrease".format(
                    rendition['resolution'].split('x')[0], rendition['resolution'].split('x')[1]),
                'c:a': 'aac',
                'ar': '48000',
                'c:v': 'h264',
                'profile:v': 'main',
                'crf': '20',
                'sc_threshold': '0',
                'g': '48',
                'keyint_min': '48',
                'hls_time': '4',
                'hls_playlist_type': 'vod',
                'b:v': f"{rendition['bitrate']}",
                'maxrate': '856k',
                'bufsize': '1200k',
                'b:a': f"{rendition['audiorate']}",
                'hls_segment_filename': f"{output_dir}/{rendition['resolution'].split('x')[1]}p_{segment_format}"
            }

            ffmpeg_output_streams.append(
                ffmpeg.output(
                    ffmpeg_input_stream,
                    f"{output_dir}/{rendition['resolution'].split('x')[1]}p.m3u8",
                    **ffmpeg_params
                )
            )

        output_streams = ffmpeg.merge_outputs(*ffmpeg_output_streams)
        ffmpeg.run(output_streams)

    def ipfs_add_dir(self, directory, pattern, recursive=True):
        with ipfshttpclient.connect() as ipfs_client:
            response = ipfs_client.add(directory, pattern=pattern, recursive=recursive)

        return response

    def ipfs_add_file(self, file_path):
        with ipfshttpclient.connect() as ipfs_client:
            response = ipfs_client.add(file_path)

        return response

    def rewrite_m3u8_files(self, ipfs_add_response):
        for item in ipfs_add_response:
            if str(item['Name']).endswith('.ts'):
                with fileinput.FileInput(f"{str(item['Name']).split('_')[0]}.m3u8", inplace=True) as file:
                    for line in file:
                        print(line.replace(str(item['Name']).split('/')[-1],
                                           f"http://127.0.0.1:8080/ipfs/{item['Hash']}"), end='')

    def generate_master_m3u8(self, output_dir, filename, ipfs_hashes):
        m3u8_content = '#EXTM3U\n#EXT-X-VERSION:3'

        for rendition in self.renditions:
            for record in ipfs_hashes:
                if str(record['Name']).split('/')[-1].replace('p.m3u8', '') == rendition['resolution'].split('x')[1]:
                    hash = record['Hash']
                    continue

            m3u8_content += f"\n#EXT-X-STREAM-INF:BANDWIDTH={str(rendition['bitrate']).replace('k', '000')}," \
                f"RESOLUTION={rendition['resolution']}\nhttp://127.0.0.1:8080/ipfs/{hash}"

        with open(f'{output_dir}/{filename}', "w") as file:
            file.write(m3u8_content)

    def preload_ipfs_gateway_caches(self):
        # Request every hash from IPFS gateways.
        pass


if __name__ == '__main__':
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
