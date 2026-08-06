# 视频生成路由

## 目录

1. Gate 3 与帧模式准入
2. 一级：Agent 自带或集成能力
3. 二级：用户指定平台 CLI
4. 三级：小云雀 CLI
5. 四级：手动生成包
6. 五级：HyperFrames 最终兜底
7. 统一回收与 QA

## 1. Gate 3 与帧模式准入

Gate 3 的首要条件不是工具可用，而是用户已经看过当前静帧并明确批准该文件
版本进入视频生成。开始前检查 `gate2-qa.md`；完整讲解片还要检查对应 beat 的
`gate2_approved=true` 与 `gate2_approved_file`。开始前的“直接跑完”、概括授权、
沉默或 Agent 自行判断都不能替代图片生成后的确认。

先读取 `frame_mode`：

- `first-last`：十套拼贴主题。输入空场首帧 + 完成态尾帧，要求平台明确支持
  first frame / end frame / tail frame。
- `single-first`：低多边形动画 `low-poly-animation`。只输入获准的起始首帧，
  要求平台明确支持单张图片的 image-to-video；不要上传或虚构尾帧。

两种模式共同要求：

- 支持 9:16 竖版或根据输入图继承比例。
- 支持 4–15 秒中的 `duration_target`，或提供不短于目标的离散时长档位。
- 能返回本地文件或可下载 URL。
- 音频不是普通 B-roll 的准入条件；模型生成什么音轨就按原样保留。只有完整
  讲解片才额外抽离音频。

只支持单图生视频的平台对拼贴模式不合格，但对低多边形模式是合格路线。

## 2. 一级：Agent 自带或集成能力

先检查当前 Agent 暴露的工具、插件、MCP 或原生视频能力：

1. 查看工具声明，按 `frame_mode` 确认首尾帧或单首帧参数及合法取值。
2. 读取 `duration_target`，匹配平台时长档位；有模型选择时展示可用模型、
   帧输入能力和预计费用，询问用户是否指定。
3. 用户没有偏好时，在实时可用且满足当前模式的模型中优先建议
   Seedance 1.5 Pro，其次 Seedance 2.0；均不可用时根据当前工具列表另行建议，
   不虚构模型。
4. 紧邻提交前展示已批准静帧版本、`frame_mode`、模型、时长、分辨率和预计
   消耗，再征得用户确认。费用无法核实时，必须取得用户对未知消耗的明确接受。
5. 提交 1 条试跑，不先批量消耗。保存真实任务 ID、平台、模型、耗时和消耗。
6. 失败后不自动换模型或重复扣费，只在再次确认后重跑失败条目。

不要因为记得某个平台“应该支持”就猜参数；以当前工具声明为准。

## 3. 二级：用户指定平台 CLI

没有 Agent 内置能力时，询问用户是否有常用平台及官方 CLI。获得后：

1. 阅读官方安装说明，运行 `<cli> --help` 和相关子命令 `--help`。
2. 只使用官方登录/授权流程，不索取 Cookie、token 或浏览器凭据。
3. 查询余额、会员要求、可用模型、图片输入参数、时长档位和预计费用。
4. 按 `frame_mode` 验证能力：拼贴必须支持尾帧；低多边形只需支持单首帧。
5. 根据 `duration-selection.md` 选择不短于目标的最小时长档位。
6. CLI 有模型可选时，先问用户是否指定；没有偏好时，只在当前实际可用且
   满足模式的模型中优先建议 Seedance 1.5 Pro，其次 Seedance 2.0。
7. 提交前展示获准静帧、模式、模型、目标/提交时长、分辨率和积分/费用并
   再次确认；费用未知时单独取得接受。
8. 保存任务 ID 并轮询到真实终态；`submitted/querying` 不等于成功。

CLI 失败时呈现真实错误，不绕过 CLI 私自调用网页接口。

## 4. 三级：小云雀 CLI

用户没有指定平台时，可推荐小云雀：

- 注册链接：<https://xiaoyunque.jianying.com/s/z_Wf-ql547E/>
- CLI 安装命令：

```bash
npx @pippit-dev/cli@latest install
```

- 当前实际可用且满足 `frame_mode` 时，模型候选优先 Seedance 1.5 Pro，
  其次 Seedance 2.0。

必须提醒用户：新用户权益、会员、积分、模型权限和费用以页面实时显示为准；
通过 CLI 正式使用前按当前流程开通最低档位会员，会员或积分由用户本人完成。

用户完成注册和会员开通后：

1. 执行官方安装与授权，读取 CLI 实时帮助。
2. 查询模型、费用、时长和图片输入能力，不凭本文件猜命令。
3. 拼贴模式只选择支持首尾帧的模型；低多边形模式选择支持单图图生视频的模型。
4. 多模型时先询问用户是否指定，再展示费用和能力差异。
5. 目标参数为 9:16、`duration_target` 对应的 4–15 秒档位、720p，以 CLI
   当前声明为准。
6. 紧邻提交前确认获准静帧、模式、模型和积分消耗；费用未知时取得明确接受。

若用户不愿注册或开通会员，进入手动生成包。

## 5. 四级：手动生成包

用户没有平台 CLI 或不愿开通小云雀时，先写英文/中文 prompt，再调用
`scripts/create_manual_package.py`。

拼贴 `first-last` 包：

```text
manual-generation/
├── README.md
├── first-frame.png
├── last-frame.png
└── video-prompt.txt
```

低多边形 `single-first` 包：

```text
manual-generation/
├── README.md
├── first-frame.png
└── video-prompt.txt
```

低多边形调用必须加：

```bash
python <本skill目录>/scripts/create_manual_package.py \
  --mode single-first --item-dir <item> \
  --prompt-en <item>/video-prompt.txt --prompt-cn <item>/video-prompt-cn.txt \
  --title "<概念名>" --duration <4-15> --duration-reason "<判定理由>"
```

README 必须写清上传文件、模式、时长、9:16、720p、关闭自动配音、验收标准
和回传原始 MP4 的要求。拼贴上传首帧后再上传尾帧；低多边形只上传首帧，
不得开启首尾帧模式。

仍可推荐用户在小云雀网页手动生成，但只选择页面实时支持当前 `frame_mode` 的
模型，并让用户在提交前查看实时积分。不要只在对话里贴 prompt，必须形成同一
目录下可直接上传的完整包。

## 6. 五级：HyperFrames 最终兜底

HyperFrames 只作为十套拼贴主题的最后兜底，并且必须同时满足：没有 Agent
视频能力、没有平台 CLI、用户不使用小云雀、已提供手动包且用户明确不会或无法
在网站生成。

拼贴执行：从确认完成态静帧分离 3–4 个大组，以实测底色建立画布，先实现静态
完成态，再用 `steps(N)` 滑入和卡位；首帧空场、结尾保持完成态，完成
`check`、快照、`render` 和 QA。明确说明它只适合刚体滑入、落位和堆叠，不能
等价实现纸张形变、穿透、碎裂或有机运动。

低多边形模式不得进入 HyperFrames 兜底。它不能等价生成低多边形 3D 人物、
拓扑稳定动作和电影镜头；没有合格平台时停在手动包，等待用户回传。

## 7. 统一回收与 QA

无论视频来自 Agent、CLI、手动网站还是 HyperFrames：

1. 保存原始视频到 `<item>/video/run-v01/final.mp4`，该文件就是交付视频。
2. 普通 B-roll 不剥离音轨。只有完整讲解片才额外创建
   `final-noaudio.mp4`；模型原片始终保留。
3. 生成逐秒 contact sheet、真实首帧和真实尾帧。
4. `first-last` 生成 `end-frame-comparison.jpg`，检查空首帧、逐件组装和尾帧
   还原；`single-first` 生成 `start-frame-comparison.jpg`，检查真实首帧与确认
   首帧，以及低多边形几何、人物身份、动作和镜头稳定性。
5. 记录 `frame_mode`、平台、模型、任务 ID、实际消耗、分辨率、帧率、
   `duration_target`、`duration_submitted`、真实时长和 QA 结论。
6. 普通 B-roll 不为统一帧率自动转码。完整讲解片保留模型原片，
   `assemble.py` 只在最终拼装过程中临时统一规格。
