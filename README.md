# zhilinhe92 — Zhilin He

这是一个 Vite 静态个人网站：默认进入 Research，另有独立的 3D Scene 和 Projects 页面。Films 暂时不展示。论文通过 JavaScript 数据文件维护，其余内容直接编辑 HTML；目前没有博客 CMS 或管理后台。内容包括六篇论文（不含书稿）、每篇论文左侧的机制图与实验同步拼贴、Generative Dynamics 与 Tennis Buddy 项目、本人照片、CV 和 Research Statement。

## 日常使用

安装 Node.js **22.12 或更高版本**，在项目根目录（能看到 `package.json` 的目录）执行。已使用 nvm 的用户可先运行 `nvm install`、`nvm use`，它们会读取项目的 `.nvmrc`：

```sh
cd /Users/zhilinhe/Documents/Codex/2026-10-02/wo/outputs/zhilinhe92
npm ci
npm run dev
```

打开终端显示的本地地址；修改源码后浏览器会更新。`Ctrl+C` 停止服务。发布前检查正式构建：

```sh
npm run build
npm run preview
```

`preview` 查看 `dist/` 中的构建结果，只用于本地预览。平时修改源码和 `public/`，不要直接编辑 `dist/`。首次安装、换电脑或 `package-lock.json` 更新后运行 `npm ci`，日常编辑只需 `npm run dev`。

| 想修改什么 | 编辑哪里 |
| --- | --- |
| 新增论文、作者、会议、摘要、预览、资源按钮 | `src/publication-data.js` |
| CV、Research Statement、社交与学术链接 | `src/profile-data.js` |
| About 文字、单位、照片说明 | `index.html` |
| 项目介绍与项目视频 | `projects.html` |
| 交互场景与人物 | `scene.html`、`src/main.js`、`blender/` |
| 图片、GIF、MP4、PDF | 放入 `public/assets/` 下合适的子目录 |
| 全站导航、标题与页脚 | 对应的各个 HTML 文件，目前没有统一模板 |

素材文件 `public/assets/example.png` 在页面和数据中写成 `./assets/example.png`，**不包含 `public/`**。使用英文小写文件名，路径大小写必须一致。

## 添加论文 / Research work

在 `src/publication-data.js` 的 `publications = [...]` 数组内增加一条记录。下面是格式示例，替换文字并放入对应素材后使用；每条之间保留逗号：

```js
{
  id: 'he2026newwork', // 全站唯一，不要复用现有论文的 id
  abbr: 'NEW WORK',
  title: '替换为论文完整标题',
  authors: [
    { name: 'Zhilin He', self: true },
    { name: '替换为合作者姓名' }, // 可加 url: 'https://真实作者主页'
  ],
  year: 2026,
  month: 10,
  selected: true,
  journal: 'arXiv preprint', // 期刊用 journal；会议用 booktitle
  tags: ['Motion planning', 'Diffusion'],
  summary: '替换为列表中显示的简短研究概述。',
  abstract: '替换为点击 Abstract 展开后的摘要。',
  method: {
    type: 'image', src: './assets/publications/new-method.png',
    alt: '原论文的机制总览图', caption: 'Method overview from the paper.',
  },
  montage: {
    type: 'video', src: './assets/publications/new-montage.mp4',
    gif: './assets/publications/new-montage.gif',
    poster: './assets/publications/new-montage.jpg',
    width: 1200, height: 900,
    alt: '所有实验同时播放的拼贴', caption: 'All experiments, shown together.',
  },
  pdf: './assets/publications/new-work.pdf',
  // code: 'https://github.com/zhilinhe92/真实仓库名', // 示例，替换为实际代码地址
  // arxiv: '真实 arXiv ID',
},
```

必须提供 `id`、`title`、`authors`、`year`、`summary`。作者的 `self: true` 用于突出本人；可用 `annotation: '*'` 标记共同一作，用论文级 `annotation` 解释。`authorLimit` 控制折叠前显示的人数（默认 6）。会议填 `booktitle`，期刊填 `journal`，学位论文可填 `school`；`venueUrl` 是会议信息的链接，`abbr` 是简短标签。录用后请同步更新真实 venue 与 BibTeX。

每篇论文左侧固定显示两项：`method` 是原论文机制图，`montage` 是把该篇全部实验同时拼进同一画面的合成动画。两张图均可点击放大，不再自动切换实验，也不生成单独的媒体墙。

网页用 H.264 MP4 播放拼贴，以减少流量并支持暂停；`gif` 字段链接到同画面的真实 GIF，放大后可下载。`poster` 是静态首帧，`width` / `height` 是合成画面尺寸。只有静态结果的论文用 `type: 'image'` 的结果拼图作为 `montage`，无需制造动画。

原始 `media` 数组保留作为合成输入及来源档案，不直接渲染。已有论文的拼贴生成脚本为 `scripts/build-publication-composites.py`，来源记录为 `public/assets/publications/gallery/composites-manifest.json`；更新实验时重新合成，再更新 `montage` 路径。脚本依赖 Python/Pillow、Node.js 和 ffmpeg；例如 `python3 scripts/build-publication-composites.py --only mga` 只重建 MGA。没有 `method` / `montage` 时兼容旧的单个 `preview`；没有图片时显示文字卡片。`video` 字段仍是资源栏中的 Video 链接。

只有进入视野的拼贴会播放，离开视野、打开大图或切到后台时暂停。页面提供全局 Pause / Play，每篇也可以单独暂停，并遵循系统减少动态效果设置。放大后可用 Escape 关闭，焦点返回原图。

填入有效地址后，相应按钮自动出现：`pdf`、`code`、`website`、`video`、`blog`、`html`、`poster`、`slides`、`supp`、`doi`、`arxiv`、`hal`。没有资源就省略字段，不必补空按钮；DOI、arXiv、HAL 可以填写 ID，其余使用真实 URL 或 `./assets/...` 路径。`abstract` 有内容才显示 Abstract。BibTeX 默认从记录生成，也可通过 `bibtex` 字段提供原始引用字符串；正式会议 / 期刊建议提供准确的 BibTeX 类型与出版信息。`award`、`badges` 仅在填写后显示，指标不会联网自动抓取。

论文按年份、月份自动排序，标题总数、年份选项、搜索、Selected 筛选、过滤结果计数和 Export bibliography 导出都会随数组更新。`public/assets/publications.bib` 是独立的静态副本，不会自动同步；如需对外分享该文件，可用最新导出替换。`index.html` 中的 `<noscript>` 论文链接也是手工内容。`index.html?q=MDOC` 可以直接打开对应搜索结果。

## About、CV、Research Statement 与个人链接

将自己的 PDF 放入 `public/assets/documents/`，然后在 `src/profile-data.js` 修改现有条目的 `url`，保留原有 `id`：

```js
export const profileDocuments = [
  { id: 'cv', label: 'CV', url: './assets/documents/cv.pdf' },
  { id: 'research-statement', label: 'Research Statement', url: './assets/documents/research-statement.pdf' },
];
```

同一文件里的 `profileLinks` 支持 Email、Google Scholar、GitHub、LinkedIn、YouTube、Bilibili、X。把相应 `url: null` 改为你自己的完整个人主页或频道地址；邮箱使用 `mailto:你的邮箱`。不要修改这些条目的 `id`，图标依赖它。文档保持 `null` 时显示 Coming soon，社交链接保持 `null` 时隐藏。

About 正文在 `index.html` 的 `.about-copy` 中。两张本人照片位于 `public/assets/portraits/`。默认展示正面大头照，点击照片切换第二张，再点击切回。替换文件或修改 `index.html` 中的图片 `src`，同时更新 `alt`；交互在 `src/portrait.js`，样式在 `src/research-about.css`。3D Scene 人物需要在 Blender 中单独替换。

## 添加项目或博客

**项目：** 在 `projects.html` 中编辑现有的 `article.project-case`。两个项目的锚点分别为 `generative-dynamics` 与 `tennis-buddy`。新增项目时复制一整块 article，更新唯一 `id`、标题、正文、代码/网站链接、视频 `source` 与 `poster`；视觉样式在 `src/projects.css`。页面顶部 `projects-jump` 的目录也需添加对应入口。项目内容不会从论文数组自动生成。

Films 暂时从导航与正式构建移除。实验视频仍在 Research 与 Projects 内播放。

**独立项目页 / 博客：** 目前没有 Markdown 到博客的自动生成或 CMS。可以复制现有内容页到根目录，例如 `blog.html`，自行替换 `<main>` 内容，修改 `<title>`、描述与导航中的 `aria-current`，并添加入口链接。**还必须在 `vite.config.js` 的 `build.rollupOptions.input` 中登记新 HTML**，否则它可能在开发时能打开，但不会进入部署构建：

```js
input: ['index.html', 'research.html', 'scene.html', 'projects.html', 'blog.html'],
```

只新增现有页面里的论文、article 或视频块，不需要改这个列表。

## 部署到 GitHub Pages

部署仓库：[hhhhzl/zhilinhe92](https://github.com/hhhhzl/zhilinhe92)。目标公开地址：[hhhhzl.github.io/zhilinhe92](https://hhhhzl.github.io/zhilinhe92/)。网站品牌是 `zhilinhe92`；GitHub owner 是 `hhhhzl`。

仓库 **Settings → Pages → Build and deployment → Source** 使用 **GitHub Actions**。推送 `main` 后，`.github/workflows/deploy.yml` 会构建并发布 `dist/`。

```sh
npm run build
git add .
git commit -m "Update research and projects"
git push origin main
```

在仓库 Actions 中检查 `Deploy to GitHub Pages`，绿色成功后打开线上地址。`node_modules/` 和 `dist/` 无需提交。

`vite.config.js` 保持 `base: './'`。图片、PDF和导航均使用相对路径，因此能在 `/zhilinhe92/` 下工作。若以后迁移到根域名 `zhilinhe92.github.io`，需要拥有 GitHub 用户或组织 `zhilinhe92`，将内容迁入其 `zhilinhe92.github.io` 仓库，再启用 Pages；修改本地目录名不会改变域名。

部署依据：[GitHub Pages 建站文档](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)、[Vite GitHub Pages 部署文档](https://vite.dev/guide/static-deploy.html#github-pages)。

以下保留场景实现、功能边界与素材来源，供技术维护和署名使用。

## The interactive Scene page

- Black, softly feathered eye housings establish the robot’s first-person view. Enlarged openings frame the human’s head, chest and gestures. A compact header provides navigation; all scene titles, explanatory copy and on-screen progress controls are removed.
- A real, textured and skinned human model replaces the former procedural figure. The Unitree G1 model retains its actual mesh and joint structure.
- The two bodies stand approximately 1.9 m apart. The five-second **Echo** source sequence plays at 0.8× speed (6.25 seconds per loop), moving from chest to outward palm to open arms with a small breathing motion. The robot's 0.12-second authored response delay becomes 0.15 seconds in playback. Camera transitions keep their original timing. It is authored choreography, not a running imitation policy or a claim about GeneDynamics results.
- Hands retain neutral wrist alignment with relaxed fingers. Stable elbow targets, at least 15° of human elbow flexion, and continuous quaternion keyframes remove wrist flips and smooth the return to standing.
- Drag **left** to rotate from the robot toward the human, and right to return. Dragging has a short inertial settle; horizontal trackpad gestures also work. Focus the canvas to use Left/Right, Home/End. The camera follows an asymmetric shoulder/hand/three-quarter path with varying elevation, lens, and slight roll.
- Space pauses/resumes movement while the canvas is focused. OS reduced-motion settings pause character animation and make camera changes immediate. Background tabs suspend rendering.
- Indigo architecture, peach light, depth of field, layered dark lens edges, subtle film grain and restrained color separation create an optical, cinematic view. The focus distance follows the actual subjects during the orbit; it no longer targets empty space between them. A smaller warm key and cooler fill preserve facial form.
- Skin uses baked micro-normal and roughness maps; the striped cotton has its own weave normal. Layered alpha-masked photographic hair cards replace the uniform tube hairstyle, and the original textured eyeballs have a separate material. The runtime retains these authored PBR settings rather than flattening every skin material to one roughness value.

## Pages and editing

| File | Purpose |
| --- | --- |
| `scene.html`, `src/main.js`, `src/scene.css` | Immersive scene, choreography playback, cinematic camera, lighting and controls |
| `index.html` | Default Research page, About, switchable portrait and publications |
| `research.html` | Compatibility redirect to Research, preserving search and hash |
| `src/publication-data.js` | Verified publication records and documented optional fields |
| `src/publications.js` | Publication renderer, search, filters, resources and citations |
| `src/publication-preview.js`, `src/publication-preview.css` | Method figure + simultaneous experiment montage, with pause and full-size viewer |
| `src/portrait.js`, `src/research-about.css` | Click-to-switch portrait and About layout |
| `src/profile-data.js` | CV, Research Statement, academic and social profile URLs |
| `src/profile.js`, `src/profile.css` | About document controls and accessible monochrome logo links |
| `projects.html`, `src/projects.css` | Generative Dynamics and Tennis Buddy case studies, original demos and links |
| `src/style.css` | Shared visual system and responsive layouts |
| `blender/zhilinhe92.blend` | Editable, packed scene and Echo animation |
| `blender/build_scene.py` | Reproducible scene construction |

### Research capabilities

The About section includes CV and Research Statement controls, followed by monochrome profile logos with keyboard-focus and hover labels. Set the two document URLs and exact account/channel URLs in `src/profile-data.js`. Local PDF paths (for example `./assets/documents/cv.pdf`) work under a GitHub Pages subdirectory. The supplied CV and Research Statement are available as local PDFs. Social accounts without a configured URL are hidden. Email, GitHub and LinkedIn use destinations from the CV. Supported logos are Email, Google Scholar, GitHub, LinkedIn, YouTube, Bilibili and X; the local SVGs and their license are under `public/assets/icons/`.

Each paper shows exactly two visuals in its left column: the original method figure and one simultaneous experiment montage. All of that paper’s clips are visible together; there is no carousel or additional media wall. The montage has identical MP4 and downloadable GIF versions; ACC uses a static results composite because its source material contains still plots. Click either visual to open a full-size dialog. Inline videos pause offscreen, while a dialog is open, and in background tabs. PDF, Code, HTML, DOI, arXiv, Abstract and BibTeX share one horizontal control strip; disclosures expand below it. On small screens the control strip scrolls horizontally without widening the page. `src/research-resources.css` owns this layout.

The research renderer follows al-folio’s publication model: authors and self highlighting, author homepage links, annotations and long-list expansion; journal/booktitle/school, month, year, location, notes; venue labels and links; selected/year/text filters; image, GIF, and video previews; full-size figures; abstract and BibTeX disclosures; citation copying and bibliography export. Direct query links such as `index.html?q=MDOC` are supported.

Resources are conditional: PDF, code, website, video, blog, HTML, poster, slides, supplement, DOI, arXiv and HAL. Awards and badges display only when explicitly supplied. Badge values are curated data, not a live Altmetric/Dimensions/Scholar integration. This is a custom publication interface, not a migration of every al-folio plugin or its Jekyll CMS.

Six records follow the supplied CV: MGA and 2GO submissions; FedGuide (CoRL Spotlight), MD-COAS (IROS), MDOC (RSS), and antivirus routing (ACC). Submission status stays distinct from accepted venues. No citation counts or unverified Scholar profile are shown. Paper figure and demo source records live in `public/assets/publications/`.

### Personal portraits and Scene performer

The Research page shows the supplied headshot, with the second photograph revealed on click. The Scene performer retains a rig derived from the MIT-licensed Microsoft Rocketbox avatar, with facial appearance adapted from the supplied portrait and a relaxed blue-and-white striped polo. This is an artistic digital approximation, not a photogrammetric scan. The choreography is independent of the publication results.

The `.blend` file includes packed image textures. Rebuilding from source also requires the original G1 asset directory and Rocketbox FBX/textures; set `G1_ASSET_DIR` to the MuJoCo Menagerie `unitree_g1` directory and `HUMAN_ASSET_DIR` to the Rocketbox library root containing `Assets/` and `LICENSE.md`. Run Blender 4.5 LTS with `--background --python blender/build_scene.py`. The exported `atelier.glb` includes all runtime meshes, textures and the single `Echo` clip.

## Asset provenance

- Unitree G1: user’s MuJoCo Menagerie checkout, BSD-3-Clause; included license.
- Microsoft Rocketbox Male_Adult_02: official library, MIT; included license and source manifest. Converted FBX to GLB, retained one LOD and authored new animation.
- Research portraits: photographs supplied by Zhilin He, used with permission for this personal website. Scene appearance: supplied face reference and the requested blue-and-white polo; avatar implementation and texture provenance in `blender/`.
- Hall: authored interpretation of the user’s laboratory footage, not a surveyed reconstruction.
- `lab-study.mp4`: user-provided `zone_a_1.mov`, 1280×592 H.264, 24 fps, 22.54 seconds, silent; available in Projects. The Research in Motion block has been removed from Research.
- Publication and project media: original figures, videos and photographs from the six papers, their project sites, and author-supplied local source assets; source records accompany the files.
- Motion/art direction references: MotionSites AI’s Monolithic / Quantum Human / Shadow 3D examples; Blank Embrace’s palette and atmospheric composition; Into the Spider-Verse’s black eye shape, print texture and motion registration. No third-party site template or painting has been copied into the site.

No backend, login, analytics or cookies are required. Google Fonts has local system font fallbacks.
