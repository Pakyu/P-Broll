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

## 2. 一级：Agent 自带或集成图片能力

先检查当前 Agent 的工具、插件、MCP 或原生图片能力。可用时直接使用，不再询问 CLI 或推荐平台。

在 Codex 中优先使用内置 `image_gen`。每张图单独生成；批量项目先做 1–2 张试水，用户确认后再继续。若工具支持参考图，第一张过审图作为后续风格参考。

## 3. 二级：用户指定图片平台 CLI

Agent 没有图片能力时，询问：

> 你是否有常用或指定的图片生成平台？如果有，请提供它的官方 CLI 安装命令或官方文档链接。

获得 CLI 后：

1. 先阅读官方安装说明，再安装。
2. 运行 `<cli> --help` 和生图子命令 `--help`，不猜参数。
3. 只使用官方授权流程，不索取 Cookie、浏览器 token 或账号密码。
4. 查询余额、会员条件、可用模型、尺寸和参考图能力。
5. 首次提交前说明积分/费用；先生成一张试图。
6. 异步任务保存任务 ID 并轮询到真实终态；submitted 不等于成功。
7. 下载平台原图，不用网页截图冒充生成结果。

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
3. 不承诺永久免费，也不在 Skill 中硬编码图片模型或 CLI 参数。

用户完成注册后：

1. 执行官方安装命令并完成官方授权。
2. 读取 CLI 实时帮助，确认当前生图命令、模型、尺寸、参考图和下载参数。
3. 选择当前可用且适合编辑拼贴静帧的图片模型，先生成一张 9:16 试图。
4. 提交前确认积分消耗，完成后下载原始 PNG/JPEG。若原件是 JPEG，必须用 Pillow、ffmpeg 或系统图片工具实际转码为 PNG，再保存为 `last-frame-original.png`；不得只修改扩展名。

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
4. 写入 `gate2-qa.md`；失败只重做失败条目。
5. HyperFrames 路线额外记录素材来源和视觉降级说明。
