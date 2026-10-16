# zhilinhe92 — Zhilin He

这是一个 Vite 静态个人网站：3D 首页，以及独立的 Research、Projects、Films 页面。论文通过 JavaScript 数据文件维护，其余内容直接编辑 HTML；目前没有博客 CMS 或管理后台。内容包括六篇论文（不含书稿）、原始实验视频画廊、Generative Dynamics 与 Tennis Buddy 项目、本人照片、CV 和 Research Statement。

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
| About 文字、单位、照片说明 | `research.html` |
| 项目介绍与项目视频 | `projects.html` |
| 独立视频展示 | `films.html` |
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
  preview: {
    src: './assets/publications/new-work.gif',
    type: 'gif',
    alt: '说明这幅图或动画展示的内容',
  },
  pdf: './assets/publications/new-work.pdf',
  // code: 'https://github.com/zhilinhe92/真实仓库名', // 示例，替换为实际代码地址
  // arxiv: '真实 arXiv ID',
},
```

必须提供 `id`、`title`、`authors`、`year`、`summary`。作者的 `self: true` 用于突出本人；可用 `annotation: '*'` 标记共同一作，用论文级 `annotation` 解释。`authorLimit` 控制折叠前显示的人数（默认 6）。会议填 `booktitle`，期刊填 `journal`，学位论文可填 `school`；`venueUrl` 是会议信息的链接，`abbr` 是简短标签。录用后请同步更新真实 venue 与 BibTeX。

静态图将 `type` 改为 `'image'`；视频预览可用下面的 `preview` 替换上例，并把文件放入 `public/assets/publications/`：

```js
preview: {
  src: './assets/publications/new-work.mp4',
  type: 'video',
  poster: './assets/publications/new-work-poster.jpg',
  alt: '研究演示视频的内容说明',
},
```

一篇论文可以另外加入 `media` 数组，在论文下方显示多组实验。每条支持 `type`、`src`、`poster`、`alt`、`caption`：

```js
media: [
  { type: 'video', src: './assets/publications/my-demo.mp4',
    poster: './assets/publications/my-demo-poster.jpg',
    alt: '描述实验内容', caption: 'Contact adaptation · simulation' },
  { type: 'image', src: './assets/publications/my-result.png',
    alt: '描述结果图', caption: 'Ablation results' },
],
```

视频在进入视野时静音循环播放，离开视野或后台时暂停；页面提供全局 Pause / Play，遵循系统减少动态效果设置。图片可点击查看原尺寸。媒体来源记录在 `public/assets/publications/` 和 `public/assets/projects/`。

MP4 建议使用网页兼容的 H.264 编码。视频预览带播放器控件；`preview` 是左侧媒体，`video` 字段则是资源栏中的 Video 链接，两者用途不同。没有图片时可省略 `preview`，页面会显示文字卡片。

填入有效地址后，相应按钮自动出现：`pdf`、`code`、`website`、`video`、`blog`、`html`、`poster`、`slides`、`supp`、`doi`、`arxiv`、`hal`。没有资源就省略字段，不必补空按钮；DOI、arXiv、HAL 可以填写 ID，其余使用真实 URL 或 `./assets/...` 路径。`abstract` 有内容才显示 Abstract。BibTeX 默认从记录生成，也可通过 `bibtex` 字段提供原始引用字符串；正式会议 / 期刊建议提供准确的 BibTeX 类型与出版信息。`award`、`badges` 仅在填写后显示，指标不会联网自动抓取。

论文按年份、月份自动排序，标题总数、年份选项、搜索、Selected 筛选、过滤结果计数和 Export bibliography 导出都会随数组更新。`public/assets/publications.bib` 是独立的静态副本，不会自动同步；如需对外分享该文件，可用最新导出替换。`research.html` 中的 `<noscript>` 论文链接也是手工内容。`research.html?q=MDOC` 可以直接打开对应搜索结果。

## About、CV、Research Statement 与个人链接

将自己的 PDF 放入 `public/assets/documents/`，然后在 `src/profile-data.js` 修改现有条目的 `url`，保留原有 `id`：

```js
export const profileDocuments = [
  { id: 'cv', label: 'CV', url: './assets/documents/cv.pdf' },
  { id: 'research-statement', label: 'Research Statement', url: './assets/documents/research-statement.pdf' },
];
```

同一文件里的 `profileLinks` 支持 Email、Google Scholar、GitHub、LinkedIn、YouTube、Bilibili、X。把相应 `url: null` 改为你自己的完整个人主页或频道地址；邮箱使用 `mailto:你的邮箱`。不要修改这些条目的 `id`，图标依赖它。文档保持 `null` 时显示 Coming soon，社交链接保持 `null` 时隐藏。

About 正文在 `research.html` 的 `.about-copy` 中。两张本人照片位于 `public/assets/portraits/`。替换文件或修改 HTML 的图片 `src`，同时更新 `alt`。这是 Research 页照片；首页 3D 人物需要在 Blender 中单独替换。

## 添加项目、影片或博客

**项目：** 在 `projects.html` 中编辑现有的 `article.project-case`。两个项目的锚点分别为 `generative-dynamics` 与 `tennis-buddy`。新增项目时复制一整块 article，更新唯一 `id`、标题、正文、代码/网站链接、视频 `source` 与 `poster`；视觉样式在 `src/projects.css`。页面顶部 `projects-jump` 的目录也需添加对应入口。项目内容不会从论文数组自动生成。

**影片：** 在 `films.html` 的 `<main>` 内，复制整块 `<section class="cinema">…</section>`，修改序号、时长、标题、说明与媒体文件。播放器本身可按下面写法替换，素材放到 `public/assets/films/`：

```html
<video controls playsinline preload="metadata"
       poster="./assets/films/my-film-poster.jpg"
       aria-label="替换为视频内容说明">
  <source src="./assets/films/my-film.mp4" type="video/mp4" />
  <p><a href="./assets/films/my-film.mp4">Open video</a></p>
</video>
```

时长与序号是手工文字，不会从视频自动读取。本地 MP4 是静态文件播放；长视频也可以链接或嵌入平台提供的官方播放器，本站没有直播后台。

**独立项目页 / 博客：** 目前没有 Markdown 到博客的自动生成或 CMS。可以复制现有内容页到根目录，例如 `blog.html`，自行替换 `<main>` 内容，修改 `<title>`、描述与导航中的 `aria-current`，并添加入口链接。**还必须在 `vite.config.js` 的 `build.rollupOptions.input` 中登记新 HTML**，否则它可能在开发时能打开，但不会进入部署构建：

```js
input: ['index.html', 'research.html', 'projects.html', 'films.html', 'blog.html'],
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

## The opening scene

- Black, softly feathered eye housings establish the robot’s first-person view. Enlarged openings frame the human’s head, chest and gestures. A compact header provides navigation; all scene titles, explanatory copy and on-screen progress controls are removed.
- A real, textured and skinned human model replaces the former procedural figure. The Unitree G1 model retains its actual mesh and joint structure.
- The two bodies stand approximately 1.9 m apart. A five-second **Echo** sequence moves from chest to outward palm to open arms; the robot responds 0.12 s later. It is authored choreography, not a running imitation policy or a claim about GeneDynamics results.
- Hands retain neutral wrist alignment with relaxed fingers. Stable elbow targets, at least 15° of human elbow flexion, and continuous quaternion keyframes remove wrist flips and smooth the return to standing.
- Drag **left** to rotate from the robot toward the human, and right to return. Dragging has a short inertial settle; horizontal trackpad gestures also work. Focus the canvas to use Left/Right, Home/End. The camera follows an asymmetric shoulder/hand/three-quarter path with varying elevation, lens, and slight roll.
- Space pauses/resumes movement while the canvas is focused. OS reduced-motion settings pause character animation and make camera changes immediate. Background tabs suspend rendering.
- Indigo architecture, peach light, depth of field, layered dark lens edges, subtle film grain and restrained color separation create an optical, cinematic view.

## Pages and editing

| File | Purpose |
| --- | --- |
| `index.html`, `src/main.js`, `src/scene.css` | Immersive homepage, choreography playback, cinematic camera, lighting and controls |
| `research.html` | About introduction and portrait above the publications; ongoing research GIF preview |
| `src/publication-data.js` | Verified publication records and documented optional fields |
| `src/publications.js` | Publication renderer, search, filters, resources and citations |
| `src/profile-data.js` | CV, Research Statement, academic and social profile URLs |
| `src/profile.js`, `src/profile.css` | About document controls and accessible monochrome logo links |
| `projects.html`, `src/projects.css` | Generative Dynamics and Tennis Buddy case studies, original demos and links |
| `films.html` | Standalone film player |
| `src/style.css` | Shared visual system and responsive layouts |
| `blender/zhilinhe92.blend` | Editable, packed scene and Echo animation |
| `blender/build_scene.py` | Reproducible scene construction |

### Research capabilities

The About section includes CV and Research Statement controls, followed by monochrome profile logos with keyboard-focus and hover labels. Set the two document URLs and exact account/channel URLs in `src/profile-data.js`. Local PDF paths (for example `./assets/documents/cv.pdf`) work under a GitHub Pages subdirectory. The supplied CV and Research Statement are available as local PDFs. Social accounts without a configured URL are hidden. Email, GitHub and LinkedIn use destinations from the CV. Supported logos are Email, Google Scholar, GitHub, LinkedIn, YouTube, Bilibili and X; the local SVGs and their license are under `public/assets/icons/`.

The original publication figure/title/authors/venue/summary layout is retained. PDF, Code, HTML, DOI, arXiv, Abstract and BibTeX share one horizontal control strip; disclosures expand below it. On small screens the control strip scrolls horizontally without widening the page. `src/research-resources.css` owns this layout.

The research renderer follows al-folio’s publication model: authors and self highlighting, author homepage links, annotations and long-list expansion; journal/booktitle/school, month, year, location, notes; venue labels and links; selected/year/text filters; image, GIF, and video previews; full-size figures; abstract and BibTeX disclosures; citation copying and bibliography export. Direct query links such as `research.html?q=MDOC` are supported.

Resources are conditional: PDF, code, website, video, blog, HTML, poster, slides, supplement, DOI, arXiv and HAL. Awards and badges display only when explicitly supplied. Badge values are curated data, not a live Altmetric/Dimensions/Scholar integration. This is a custom publication interface, not a migration of every al-folio plugin or its Jekyll CMS.

Six records follow the supplied CV: MGA and 2GO submissions; FedGuide (CoRL Spotlight), MD-COAS (IROS), MDOC (RSS), and antivirus routing (ACC). Submission status stays distinct from accepted venues. No citation counts or unverified Scholar profile are shown. Paper figure and demo source records live in `public/assets/publications/`.

### Personal portraits and homepage performer

The Research page uses the two supplied photographs of Zhilin He. The homepage performer retains a rig derived from the MIT-licensed Microsoft Rocketbox avatar, with appearance adapted from the supplied face and outfit references. This is an artistic digital approximation, not a photogrammetric scan. The choreography is independent of the publication results.

The `.blend` file includes packed image textures. Rebuilding from source also requires the original G1 asset directory and Rocketbox FBX/textures; set `G1_ASSET_DIR` to the MuJoCo Menagerie `unitree_g1` directory and `HUMAN_ASSET_DIR` to the Rocketbox library root containing `Assets/` and `LICENSE.md`. Run Blender 4.5 LTS with `--background --python blender/build_scene.py`. The exported `atelier.glb` includes all runtime meshes, textures and the single `Echo` clip.

## Asset provenance

- Unitree G1: user’s MuJoCo Menagerie checkout, BSD-3-Clause; included license.
- Microsoft Rocketbox Male_Adult_02: official library, MIT; included license and source manifest. Converted FBX to GLB, retained one LOD and authored new animation.
- Research portraits: photographs supplied by Zhilin He, used with permission for this personal website. Homepage appearance: supplied face and outfit references; avatar implementation and texture provenance in `blender/`.
- Hall: authored interpretation of the user’s laboratory footage, not a surveyed reconstruction.
- `lab-study.mp4`: user-provided `zone_a_1.mov`, 1280×592 H.264, 24 fps, 22.54 seconds, silent. `lab-preview.gif` is a 4-second, 480×222, 9 fps excerpt; reduced-motion users receive a still image. `lab-poster.jpg` derives from `zone_a_stand.png`.
- Publication and project media: original figures, videos and photographs from the six papers, their project sites, and author-supplied local source assets; source records accompany the files.
- Motion/art direction references: MotionSites AI’s Monolithic / Quantum Human / Shadow 3D examples; Blank Embrace’s palette and atmospheric composition; Into the Spider-Verse’s black eye shape, print texture and motion registration. No third-party site template or painting has been copied into the site.

No backend, login, analytics or cookies are required. Google Fonts has local system font fallbacks.
