# MKV Splitter for Kinesis Video Streams

A lightweight Python script to split concatenated MKV fragments into separate files.

This is designed for segmenting video streams retrieved from the [Kinesis Video Streams GetMedia API](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_GetMedia.html),
where multiple MKV fragments are written sequentially in a single file or stream.

---

## Requirements

- This script was written and tested with Python 3.12.
- This script has no external dependencies.

---

## Usage

```bash
python3 ./split_mkv.py --help
```

Output files are saved to `./output/split_output_<n>.mkv` by default.
Use `--output-prefix` to customize the path and prefix.

Add `--verbose` to enable detailed debug logging.

### From a local MKV file

```bash
python3 ./split_mkv.py --input ~/Downloads/get-media-output.mkv
```

### Pipe from stdin

```bash
cat ~/Downloads/get-media-output.mkv | python3 ./split_mkv.py
```

<details><summary>Sample output</summary>

```log
cat ~/Downloads/get-media-output.mkv | python3 ./split_mkv.py
2025-04-10 09:55:42,221 - INFO - Reading from stdin...
2025-04-10 09:55:42,325 - INFO - Created: ./output/split_output_0.mkv (903.29 KB)
2025-04-10 09:55:42,326 - INFO - Created: ./output/split_output_1.mkv (426.20 KB)

Summary of created files:
+-----------------------------+-----------+
| File Name                   | Size      |
+-----------------------------+-----------+
| ./output/split_output_0.mkv | 903.29 KB |
| ./output/split_output_1.mkv | 426.20 KB |
+-----------------------------+-----------+
```

</details>

---

## How it works

- When you run GetMedia and GetMediaForFragmentList, it returns multiple fragments. They are appended in a single byte stream with no delimiters. 
- As such, the recommended approach is to use an EBML parser to split the fragments.
- A more light-weight approach (this script) would be just to scan the input for only the EBML header start byte sequence: `0x1A 0x45 0xDF 0xA3`

> [!NOTE]
> It is possible for this same byte sequence to appear inside frame data, so this heuristic is not guaranteed to work for all MKV streams.


