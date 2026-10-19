# Simultaneous experiment composites

Author-provided research material, reused at the author’s request. Retain upstream paper and repository terms; this record does not grant a new license. Prior publication figure licensing is recorded separately in sources.json.

Each animation shows every available experiment for that paper at once. Videos retain their source speed; shorter clips loop independently while the longest completes. This is a presentation collage, not evidence that experiments occurred in sync. No input frame is newly cropped; original clips may contain pre-existing crops or time normalization documented in [the original source manifest](../gallery-sources.json).

The GIF and H.264 MP4 for each paper show the same montage. MP4 is the lightweight browser playback version. JPEG posters are the first decoded frame. ACC has only its original static experiment-results figure and therefore has no fabricated animation.

| Paper | Inputs | Outputs |
| --- | ---: | --- |
| mga | 9 | [mga-experiments.mp4](mga-experiments.mp4) · [mga-experiments.gif](mga-experiments.gif) · [mga-experiments.jpg](mga-experiments.jpg) |
| 2go | 7 | [2go-experiments.mp4](2go-experiments.mp4) · [2go-experiments.gif](2go-experiments.gif) · [2go-experiments.jpg](2go-experiments.jpg) |
| fedguide | 8 | [fedguide-experiments.mp4](fedguide-experiments.mp4) · [fedguide-experiments.gif](fedguide-experiments.gif) · [fedguide-experiments.jpg](fedguide-experiments.jpg) |
| md-coas | 7 | [md-coas-experiments.mp4](md-coas-experiments.mp4) · [md-coas-experiments.gif](md-coas-experiments.gif) · [md-coas-experiments.jpg](md-coas-experiments.jpg) |
| mdoc | 6 | [mdoc-experiments.mp4](mdoc-experiments.mp4) · [mdoc-experiments.gif](mdoc-experiments.gif) · [mdoc-experiments.jpg](mdoc-experiments.jpg) |
| acc | 1 | [acc-results-composite.png](acc-results-composite.png) · [acc-results-composite.jpg](acc-results-composite.jpg) |

Animated montages use a consistent 1280 px width, 8 px outer framing/gutters, equal tiles within each paper, centered short rows, and 30 px caption bands. Image cells follow the natural proportions of each paper’s clips; canvas height follows those rows, avoiding extra outer padding. Framing, captions and newly introduced letterboxing are muted indigo (#30394e). Original source colors, including scientific white backgrounds, are preserved. Visible captions abbreviate repeated context; the complete original captions remain in the manifest.

Per-input original URLs/local provenance, hashes, complete placement coordinates, dimensions, timing and transformations are in [composites-manifest.json](composites-manifest.json). Reproduction script: `scripts/build-publication-composites.py` at the repository root (requires Python/Pillow, Node.js, ffmpeg and the original local media arrays/assets). Use `--preview --output-dir /tmp/montage-review` to inspect layouts without replacing public media.
