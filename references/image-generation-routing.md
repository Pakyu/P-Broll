# 图片生成路由

Gate 2 生成最终静帧时读取本文件。一旦某级可用就停止向下寻找。

## 目录

1. 通用输出要求
2. 一级：Agent 自带或集成图片能力
3. 二级：用户指定图片平台 CLI
4. 三级：小云雀
5. 四级：HyperFrames 最终兜底
6. 统一回收与 QA

## 1. 通用输出要求

- 输出 9:16 PNG，目标 1080×1920；平台只支持相近尺寸时保留原图并记录实际尺寸。
- 最终文件保存为 `<item>/frames/last-frame-original.png`。
- 完整 prompt 保存为 `<item>/imagegen-prompt.txt`。
- 禁止可读文字、数字、logo、水印、UI、字幕和未经授权的品牌素材。
- 首次付费或扣积分前展示平台、模型、尺寸、张数和预计消耗并征得用户确认。
- 失败后呈现真实错误，不自动换模型或重复提交。
- CLI 提供多个模型时，先询问用户是否指定；没有偏好时再结合平台当前价格、能力和本项目画面需求推荐。
- 推荐候选仅在平台实时列表确实存在时使用：**Seedream 5.0 Pro、NanoBanana、GPT Image 2**。不要假设型号一定可用，也不要把候选顺序伪装成固定质量或价格排名。
- 费用无法从 CLI 或官方页面可靠核实时，明确标记“费用未知”；只有用户明确接受未知消耗后才提交。
- 所有生成式图片调用都采用纯文生图。不得把已生成图片或其派生图作为后续生图输入；同批风格一致性通过完整文字规范、色板和构图参数维持。HyperFrames 仅作为初始静帧的非生成式兜底，不能用于修改已经展示过的图片。

## 2. 一级：Agent 自带或集成图片能力

先检查当前 Agent 的工具、插件、MCP 或原生图片能力。可用时直接使用，不再询问 CLI 或推荐平台。

在 Codex 中优先使用内置 `image_gen`。每张图单独纯文生图；批量项目先做 1–2 张试水，用户确认后再继续。后续图片复用锁定后的文字风格描述，不把试水图作为参考输入。

## 3. 二级：用户指定图片平台 CLI

Agent 没有图片能力时，询问：

> 你是否有常用或指定的图片生成平台？如果有，请提供它的官方 CLI 安装命令或官方文档链接。

获得 CLI 后：

1. 先阅读官方安装说明，再安装。
2. 运行 `<cli> --help` 和生图子命令 `--help`，不猜参数。
3. 只使用官方授权流程，不索取 Cookie、浏览器 token 或账号密码。
4. 查询余额、会员条件、可用模型、尺寸、纯文生图参数和各模型预计积分/费用。
5. CLI 有模型选择时，先问用户是否指定。用户没有想法时，只在实时可用列表中考察 Seedream 5.0 Pro、NanoBanana、GPT Image 2，并说明推荐理由与价格差异。
6. 首次提交前说明模型、积分/费用和张数；先生成一张试图。无法核实费用时，取得用户对未知消耗的明确接受。
7. 仅传文字 prompt，不上传现有图片、截图、蒙版、控制图或其他参考图。
8. 异步任务保存任务 ID 并轮询到真实终态；submitted 不等于成功。
9. 下载平台原图，不用网页截图冒充生成结果。

CLI 失败时呈现真实错误，不绕过 CLI 私自调用未公开网页接口。

## 4. 三级：小云雀

用户没有指定图片平台时，推荐小云雀：

- 注册链接：<https://xiaoyunque.jianying.com/s/z_Wf-ql547E/>
- CLI 安装命令：

```bash
npx @pippit-dev/cli@latest install
```

必须提醒用户：

1. 新用户可能有免费积分，以小云雀页面实时显示为准。
2. 通过 CLI 正式使用前，按当前既定流程提醒用户开通最低档位会员；会员和积分由用户本人完成。
3. 不承诺永久免费，也不猜测 CLI 参数或模型可用性。

用户完成注册后：

1. 执行官方安装命令并完成官方授权。
2. 读取 CLI 实时帮助，确认当前纯文生图命令、可用模型、尺寸、下载参数和模型费用。
3. 有多个模型时先问用户是否指定。用户没有想法时，只在实时存在的模型中优先考察 Seedream 5.0 Pro、NanoBanana、GPT Image 2，再依据价格与画面需求提出一个建议。
4. 展示模型、尺寸、张数和预计积分/费用，取得确认后只提交文字 prompt，先生成一张 9:16 试图；费用未知时必须明确说明并单独取得接受。
5. 完成后下载原始 PNG/JPEG。若原件是 JPEG，必须用 Pillow、ffmpeg 或系统图片工具实际转码为 PNG，再保存为 `last-frame-original.png`；不得只修改扩展名。

用户不使用 CLI 时，可把 `imagegen-prompt.txt` 交给用户在小云雀网页手动生成；仍提供注册链接。网页会员条件、模型和免费积分以页面实时显示为准。用户回传原图后再进入 Gate 2 QA。

## 5. 四级：HyperFrames 最终兜底

仅在 Agent 没有图片能力、用户没有可用平台 CLI，且不使用小云雀网页时进入。使用已安装的 `hyperframes` Skill 和当前 HyperFrames CLI。

HyperFrames 是确定性 HTML 合成，不是生成式图片模型。它能可靠完成：

- 平坦色场、卡纸、奶油色 keyline、阴影和纸张纹理。
- CSS/SVG 几何物件、抽象波浪线、图标式隐喻和已有本地素材排版。
- 对用户提供且有权使用的照片做黑白、对比度、裁切和半调视觉处理。

它不能凭空生成摄影人物、真实物件或复杂场景。缺少合法主体素材时，改用抽象纸片/SVG 隐喻并向用户说明视觉降级。

执行流程：

1. 在 `<item>/hyperframes-still/` 创建单场景 1080×1920 composition。
2. 把 Gate 1/1.5 锁定的色板、纸张质感和构图写入 `frame.md`；先完成静态 hero frame，不添加不必要动画。
3. 使用 HyperFrames 规则编写 `index.html`，只引用项目内合法素材。
4. 运行 `npx hyperframes lint` 与 `npx hyperframes validate`。
5. 先运行 `npx hyperframes snapshot --help`，确认当前版本参数；支持时执行：

```bash
npx hyperframes snapshot <item>/hyperframes-still \
  --at=0.5 --no-end --describe=false \
  --output=<item>/hyperframes-still/snapshots
```

6. 检查实际生成的 PNG，选择通过 QA 的一张复制为 `<item>/frames/last-frame-original.png`。
7. 记录 `image_generation_route=hyperframes`、`image_generation_platform=local`、`image_generation_model=deterministic-html-snapshot`。

不要依赖 `snapshot` 的固定文件名；不同版本可能变化，应在输出目录中检查真实文件。当前 CLI 没有 `snapshot` 时，读取实时帮助寻找等价的官方 PNG 截帧能力；没有等价能力则报告阻塞，不发明命令。

## 6. 统一回收与 QA

无论图片来自 Agent、平台 CLI、小云雀网页还是 HyperFrames，都执行：

1. 保留供应商原图或 HyperFrames composition 源文件。
2. 标准交付路径使用 `<item>/frames/last-frame-original.png`。
3. 检查尺寸、隐喻、构图、色场、纸张质感、假字、logo、水印、UI 和主体组数。
4. 把实际图片展示给用户，明确询问是否批准该版本进入视频生成。把获准文件名和用户确认内容写入 `gate2-qa.md`；没有明确确认就停止在 Gate 2。
5. 用户要求修改时，保留旧版本，把反馈合并进一份全新的完整 prompt，使用纯文生图重新生成新版本。禁止使用旧图、裁剪图、截图、蒙版、控制图或任何派生图进行 image-to-image、局部重绘、扩图或参考图修改。
6. 当前路线不能纯文生图时，切换到可纯文生图的路线；没有可用路线时报告阻塞。HyperFrames 初始兜底图被要求修改时，也不得编辑旧 composition 或基于旧图修改，必须转纯文生图路线重新生成。
7. 每个新版本都重新 QA、展示并确认；旧版本确认不得继承。完整讲解片回填 `gate2_approved=true`、`gate2_approved_file` 和 `gate2_approval_note`。
8. HyperFrames 路线额外记录素材来源和视觉降级说明。
