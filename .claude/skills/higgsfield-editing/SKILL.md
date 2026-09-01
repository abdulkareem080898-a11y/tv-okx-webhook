# Higgsfield Editing & Generation Skill

Trigger: load this skill when the user asks to generate images, generate videos, edit images, edit videos, upscale, remove backgrounds, reframe, outpaint, or use any Higgsfield AI generation feature.

---

## Quick Model Reference

### Images — best quality picks
| Goal | Model ID | Max res |
|---|---|---|
| 4K photorealistic / text / diagrams | `nano_banana_pro` | 4K |
| 4K general + editing | `gpt_image_2` | 4K (`resolution:"4k"`, `quality:"high"`) |
| Fast high-quality | `nano_banana_2` | 4K |
| Expressive / high-contrast | `grok_image` | 2K (`mode:"quality"`) |
| Portrait / fashion / editorial / UGC | `soul_2` | — |
| Commercial / product / ads | `marketing_studio_image` | — |

### Videos — best quality picks
| Goal | Model ID | Notes |
|---|---|---|
| General text-to-video / reference consistency | `seedance_2_5` | `resolution:"1080p"`, `bitrate_mode:"high"` |
| Multi-shot / audio / motion transfer | `kling3_0` | — |
| 2K keyframes + image/video/audio refs | `minimax_h3` | — |
| Marketing / product ads | `marketing_studio_video` | — |

---

## Image Generation — Step by Step

1. **Choose the model** from the table above. When unsure, call `models_explore(action:"recommend")` with a brief goal description.
2. **Call `generate_image`** with these quality defaults:
   - `nano_banana_2` / `gpt_image_2`: set `resolution:"4k"` (and `quality:"high"` for GPT Image 2)
   - `grok_image`: set `mode:"quality"`
   - Use `count:2-4` for variants of the same prompt.
3. **For editing an existing image** (inpaint, image-to-image): pass `medias:[{value:"<media_id>", role:"image_references"}]` and set `is_inpaint:true` if masking.
4. **Upload local files** with `media_upload_widget` before referencing them. For web URLs use `media_import_url` first.

### High-quality prompt formula
```
[subject], [style/medium], [lighting], [composition/angle], [color palette], [quality keywords]
```
Example:
> "A golden retriever sitting in a sunlit café, photorealistic, cinematic side lighting, close-up portrait, warm amber tones, 4K ultra-detailed, sharp focus"

---

## Video Generation — Step by Step

1. **Pick the model**. Default: `seedance_2_5` for most tasks.
2. **Call `generate_video`** with these quality defaults:
   - `seedance_2_5`: `resolution:"1080p"`, `bitrate_mode:"high"`, `generate_audio:true`
   - `duration`: start at `5` seconds; go up to `30` for longer scenes.
   - `aspect_ratio`: `"16:9"` (landscape) or `"9:16"` (TikTok/Reels/Shorts).
3. **For image-to-video**: pass your image as `medias:[{value:"<media_id>", role:"start_image"}]`.
4. **For video editing**: use `mode:"video_edit"` with a reference video + edit prompt.
5. **For video extension**: use `mode:"video_extension"` + `extension_mode:"forward"` or `"backward"`.

### High-quality prompt formula for video
```
[scene description], [camera movement], [lighting], [mood/atmosphere], [style]
```
Example:
> "A woman walking through a neon-lit Tokyo street at night, slow dolly forward, dramatic neon reflections on wet pavement, cinematic noir mood, photorealistic"

---

## Editing Tools (post-generation)

| Task | Tool |
|---|---|
| Upscale image to 2K/4K | `upscale_image` |
| Upscale video to 2K/4K | `upscale_video` |
| Remove background (cutout) | `remove_background` |
| Expand / uncrop an image | `outpaint_image` |
| Change aspect ratio | `reframe` |
| Apply motion / puppeteer | `motion_control` |

Always prefer these dedicated tools over re-generating when you already have an asset.

---

## Specialized Workflows (load before generating)

Call `get_workflow_instructions(workflow:"<name>")` before starting any of these:

| Workflow | When to use |
|---|---|
| `video-editing` | Real-footage edits, timelines, captions, b-roll |
| `thumbnail-generation` | YouTube / Instagram thumbnails |
| `product-photoshoot` | Product photography, packshots, lifestyle stills |
| `faceless-video` | Narrated explainer / story / educational videos |
| `ugc-review-video` | Talking-head creator review/ad |
| `ugc-product-video` | Product-only UGC (no on-camera creator) |
| `ad-multiplier` | Multiple edited ad variations from one 4-30s clip |
| `character-sheet` | Character reference sheets, model sheets, turnarounds |
| `brand-asset-creation` | Logos, brand kits, mockups, packaging |

---

## Common Flows

### Generate a 4K image
```
1. generate_image({ model:"nano_banana_2", prompt:"...", params:{ resolution:"4k" }, aspect_ratio:"16:9" })
```

### Generate a 1080p video from text
```
1. generate_video({ model:"seedance_2_5", prompt:"...", params:{ resolution:"1080p", bitrate_mode:"high", generate_audio:true, duration:5 }, aspect_ratio:"16:9" })
```

### Image → video (animate a photo)
```
1. media_import_url(url:"<image_url>")  →  returns media_id
2. generate_video({ model:"seedance_2_5", medias:[{value:"<media_id>", role:"start_image"}], prompt:"...", params:{ resolution:"1080p", bitrate_mode:"high" } })
```

### Upscale after generation
```
1. upscale_image / upscale_video with the job_id from the previous generation
```

---

## Cost & Credits

- Call `generate_image` or `generate_video` with `get_cost:true` to preflight the credit cost before spending.
- Never set `use_unlim:true` unless the user explicitly asks to spend their free-trial unlimited generations.
- Models marked `supports_unlim` accept free-trial generations: `gpt_image_2`, `nano_banana_2`.

---

## Tips for Best Quality

- **Images**: prefer `4k` resolution + detailed prompts with lighting, composition, and style descriptors.
- **Videos**: use `1080p` + `bitrate_mode:"high"` + explicit camera movement in the prompt.
- **Consistency**: use `soul_2` + a `soul_id` for a reusable trained character across generations.
- **Editing**: always try the dedicated edit tool (`outpaint_image`, `remove_background`, etc.) before regenerating — they preserve the original asset's quality.
- **Previewing cost**: always `get_cost:true` first on expensive 4K or long-duration jobs.
