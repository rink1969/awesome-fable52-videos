# -*- coding: utf-8 -*-
"""
Build script for awesome-fable5-2-videos.

Source of truth: the ENTRIES list below (curated manually from X on 2026-11-10,
the day Claude Fable 5.2 launched). Running this script regenerates:

  - data/videos.json   (structured data, one object per video)
  - prompts/<slug>.md  (one prompt file per video)
  - README.md          (the awesome list)

Usage:  python tools/build.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORIES = {
    "official": "Official",
    "motion": "Motion graphics",
    "3d": "3D scenes",
    "games": "Games & interactive",
    "explainer": "Explainers",
}

# The full "AI 全自动 3D 电影制作提示词" shared by @JamesDa55049936 (Chinese
# rendering of the one prompt Riley Brown gave Fable 5.2 for the Clawd 4K
# short; the English original lives in Riley's claude.ai making-of page).
CLAWD_4K_PROMPT = """你是一名世界级的 3D 动画导演、Blender 技术艺术家、Python 开发工程师和电影后期制作专家。
你的任务：仅通过编写代码，独立制作一部具有电影级质感的 4K 3D 动画短片。

一、场景构建
使用 Blender 和 Python（bpy）自动创建完整的 3D 场景。
场景设定为一间温暖、现代、极简主义风格的创作者工作室，包含：
一张具有真实木质纹理的办公桌
一台精细建模的 MacBook，包含键盘、触控板和屏幕
台灯、装饰物以及富有生活气息的工作室细节
一个可爱的 Clawd 3D 吉祥物角色，具备完整的动画控制系统
具有真实光影、反射、材质和景深的电影级环境

二、动态电脑屏幕
使用 HTML、CSS 和 JavaScript 创建一个外观接近 Claude 应用的交互式网页。
将网页内容以动画纹理的方式呈现在 3D 场景中的 MacBook 屏幕上。
屏幕必须能够真实展示 AI 对话、代码逐字生成、界面滚动、光标移动以及任务完成等动态过程。

三、电影级镜头与动画
整部短片设计 13 个独立镜头，利用程序化动画完成镜头运动、角色表演和环境变化。
镜头包含：
金色夕阳照进工作室，缓慢推进的全景镜头。
摄像机环绕桌面，展现完整的 3D 环境。
特写 MacBook，屏幕逐渐亮起。
Claude 风格的界面出现，开始生成代码。
键盘按键逐个下压，模拟真实打字。
Clawd 从桌面一侧跳入画面。
Clawd 好奇地观察正在运行的 AI。
摄像机跟随 Clawd 在桌面上跳跃。
太阳逐渐落下，房间进入蓝调时刻。
夜幕降临，电脑屏幕和台灯成为主要光源。
AI 持续工作，Clawd 与屏幕产生趣味互动。
清晨的第一缕阳光重新照进房间。
镜头缓缓拉远，以温暖的日出和最终标题结束。
所有动画必须具有自然的运动曲线、合理的物理表现和流畅的镜头衔接。

四、灯光与时间变化
构建动态昼夜光照系统，实现：
金色夕阳 → 日落 → 蓝调时刻 → 深夜 → 黎明 → 金色日出。
确保阳光方向、环境亮度、物体阴影、材质反射及室内灯光随时间自然变化。

五、自动化渲染
使用 Blender Cycles 渲染引擎，目标输出为：
分辨率：3840 × 2160（4K UHD）
帧率：24 FPS
真实电影级灯光和材质
高质量降噪与色彩管理
自动化镜头渲染与视频合成
编写完整的 Python 脚本，实现无人值守的场景生成、动画配置、相机切换及分布式渲染。
设计兼容 RunPod 的渲染流程，支持调度最多 10 张 GPU 进行并行渲染。
优化目标：尽可能接近 52 分钟完成渲染、GPU 总成本控制在 5.75 美元以内。
这些是优化目标，而非必须保证的结果；请根据实际 GPU 型号、价格和场景复杂度估算可行性。

六、音乐和音效
使用 ElevenLabs 或类似工具生成与画面同步的原创背景音乐和音效。
音效包含键盘敲击、Clawd 跳跃、轻微机械声、界面反馈声和自然环境声。
音乐从温暖、轻快逐渐转向夜晚的宁静与科技感，最终在日出时达到充满希望的情绪高潮。

七、自动后期制作
完成全部镜头后，自动执行：
13 个镜头的剪辑与衔接
统一的电影级调色
音乐、环境音和音效混合
优雅的动态字幕与片尾标题
最终 MP4 视频导出

八、交付要求
交付可运行的 Blender Python 项目、所有必要的资产生成脚本、网页屏幕内容、动画时间轴、渲染和合成脚本，以及最终成片。
优先采用程序化生成方案，减少人工建模、手动打关键帧和人工剪辑。
最重要的要求：你不仅需要规划这部动画，还需要实际编写代码、执行流程、发现并修复错误，尽可能独立完成整部 4K 3D 动画短片。
最终视觉风格：电影级 3D 渲染、温暖治愈、富有科技感、精致的微缩世界美学，配合自然流畅的角色动画和具有叙事感的镜头语言。"""

# ---------------------------------------------------------------------------
# Curated entries. One dict per video.
#
# Fields:
#   slug       unique id, <handle>-<last 6 digits of status id>
#   author     X handle
#   name       display name (defaults to @handle)
#   status     status id (builds post_url)
#   title      short English title for the README table
#   category   official | motion | 3d | games | explainer
#   tech       list of tech tags
#   prompt     the shared prompt (verbatim) or the original post text
#   partial    True when `prompt` is NOT a real reusable prompt
#   likes      like count at collection time (optional)
#   views      view count at collection time (optional)
#   duration   video length, e.g. "0:58" (optional)
#   note       extra context shown in the prompt file (optional)
# ---------------------------------------------------------------------------

ENTRIES = [
    # ------------------------------------------------------------- Official
    dict(
        slug="claudeai-268322", author="claudeai", name="Claude",
        status="2119867114450268322",
        title="Introducing Claude Fable 5.2 and Claude Mythos 5.2",
        category="official", tech=["launch"],
        prompt="Introducing Claude Fable 5.2 and Claude Mythos 5.2, designed to tackle the most daunting technical challenges. They’re capable collaborators on ambitious projects in many fields, and show improvements in areas like coding, reasoning, and vision.",
        partial=True, likes=85962, views=11583122, duration="0:19",
        note="The official launch video. Everything else in this list was inspired by it.",
    ),

    # -------------------------------------------------------- 3D scenes
    dict(
        slug="rileybrown-537708", author="rileybrown", name="Riley Brown",
        status="2119902109709537708",
        title="Clawd & Claude — a 4K 3D animated short from ONE prompt ($5.75, 52 min)",
        category="3d", tech=["Blender", "Python", "RunPod", "ElevenLabs", "4K"],
        prompt=CLAWD_4K_PROMPT,
        partial=False, likes=4418, views=398380, duration="0:55",
        note=("Done live on stream. One prompt: Fable wrote Blender code for the whole room "
              "(desk, MacBook, light, Clawd), built the laptop screen as a Claude-app lookalike web page, "
              "animated 13 camera shots with a golden-hour-to-sunrise light cycle, rented 10 GPUs on RunPod, "
              "rendered 4K in 52 minutes for $5.75, then graded, titled and scored it with ElevenLabs.\n"
              "Prompt above is the full Chinese rendering shared by @JamesDa55049936 "
              "(https://x.com/JamesDa55049936/status/2120013859771859451); "
              "Riley's English original and making-of are on his claude.ai page ('The Edge Making-Of')."),
    ),
    dict(
        slug="jeremyberman-712206", author="jeremyberman", name="Jeremy Berman",
        status="2119869358679712206",
        title="Welcome Fable 5.2, creator of worlds",
        category="3d", tech=["Blender", "Python"],
        prompt="Welcome Fable 5.2, creator of worlds",
        partial=True, likes=1210, views=162022, duration="0:18",
        note=("Posted alongside the launch announcement. Widely re-shared — e.g. @alexmichael: "
              "'Claude Fable 5.2 made this entire video from scratch, writing Python to control Blender' "
              "(1,546 likes) and @bangbuilds' commentary on the dinosaur short."),
    ),
    dict(
        slug="lexnlin-577333", author="LexnLin", name="Leon Lin",
        status="2119880654858977333",
        title="High-speed-camera 3D scene in ~30 minutes with a few Opus 5.5 subagents",
        category="3d", tech=["3D", "subagents"],
        prompt="wow, this took ONLY about 30minutes with Fable 5.2 and a few opus 5.5 subagents",
        partial=True, likes=1467, views=100450, duration="0:26",
        note=("The most re-shared community video of launch day — @AndyL5cc (68 likes), "
              "@feishutoday (41 likes) and @guanmo_ai all posted it."),
    ),
    dict(
        slug="yxzrainy-595551", author="YxzRainy", name="兴雨",
        status="2119928520595935551",
        title="Fable 5.2 + Opus 5.5 sub-agents — high-speed-camera 3D scene in 30 min",
        category="3d", tech=["3D", "subagents"],
        prompt="我尼玛😱！开什么玩笑？？？\n\nFable 5.2 加几个 Opus 5.5 子 Agent，30 分钟就能做出这种高速运镜的 3D 场景？？？\n\n这真的不是用其他工具提前渲染出来的？？？",
        partial=True,
    ),
    dict(
        slug="yxzrainy-555281", author="YxzRainy", name="兴雨",
        status="2119936069877555281",
        title="《Sky》-like aesthetics — light, color and atmosphere",
        category="3d", tech=["3D", "aesthetics"],
        prompt="感受一下 Claude Fable 5.2 的顶级审美 😭 这光影、配色和氛围感，真有《光遇》那味儿了好吧…… 有一说一，这审美 ChatGPT 得学十年 🤣 👌",
        partial=True, likes=48, views=3318, duration="0:57",
    ),
    dict(
        slug="stefan-3d-ai-694165", author="Stefan_3D_AI", name="Stefan 3D AI",
        status="2120041169719894165",
        title="September castle prompt re-run: Fable 5.2 vs Opus 5.5 (procedural Blender)",
        category="3d", tech=["Blender", "procedural", "comparison"],
        prompt="The difference between Fable 5.2 and Opus 5.5 is really noticeable. I re-ran my castle prompt from September on both: Blender only, all procedural. Look at the amount of detail in Fable's shot and how clean it is. What a jump. Fable 5.2: 71 min, 380k output tokens, about $32.9",
        partial=True, likes=50, views=2298, duration="0:31",
    ),
    dict(
        slug="getviewgum-587264", author="getviewgum", name="Viewgum",
        status="2119991792053387264",
        title="Fable 5.2 vs Opus 5.5 in viral 3D video generation",
        category="3d", tech=["3D", "comparison"],
        prompt="Fable 5.2 vs Opus 5.5 in Viral 3D Video Generation",
        partial=True, likes=53, views=2323, duration="0:47",
    ),
    dict(
        slug="aimlapi-409682", author="aimlapi", name="AI/ML API",
        status="2119889097053409682",
        title="Cars Piston Cup finale re-created in 3D voxels ($108.87) — vs GPT-6.1 Sol",
        category="3d", tech=["voxels", "3D", "comparison"],
        prompt="Fable 5.2 vs GPT-6.1 Sol at Cars movie 🏁 Fable 5.2 re-created the Cars Piston Cup finale in 3D voxels for $108.87 while GPT-6.1 Sol's version cost $13.02",
        partial=True, likes=732, views=285870, duration="0:39",
    ),
    dict(
        slug="leo114119-141745", author="leo114119", name="Leo · Building w/ AI",
        status="2119934826111451495",
        title="Istanbul re-created in 3D, straight from code",
        category="3d", tech=["3D", "city"],
        prompt="Fable 5.2 直接用 3D 还原了整个城市\n\n土耳其的伊斯坦布尔\n\n还有比更疯狂的吗？\n\nFable 5.2 感觉完全是领先一个级别的模型啊。。。",
        partial=True,
    ),
    dict(
        slug="leo114119-515723", author="leo114119", name="Leo · Building w/ AI",
        status="2119932921415151723",
        title="Immersive 3D black-hole simulation in pure code",
        category="3d", tech=["3D", "simulation", "pure-code"],
        prompt="Fable 5.2 纯代码生成的 3D 黑洞模拟动画\n\n感觉就好像正在被黑洞吸进去一样。。。\n\n这沉浸感也太强了吧。。",
        partial=True,
    ),
    dict(
        slug="leo114119-883350", author="leo114119", name="Leo · Building w/ AI",
        status="2119950111958831350",
        title="Hyper-realistic Blender 3D video — 'the 3D-movie era for everyone?'",
        category="3d", tech=["Blender", "3D"],
        prompt="Claude Fable 5.2 +Blender 生成的 3D 视频\n\n这 TMD 也太真实了吧。。。\n\n人人都可以做 3D 电影的时代要到来了？",
        partial=True,
    ),
    dict(
        slug="leo114119-347445", author="leo114119", name="Leo · Building w/ AI",
        status="2119934353367347445",
        title="Voxel floating pagoda — detail to the point of madness",
        category="3d", tech=["voxels", "3D"],
        prompt="Fable 5.2构建的 3D 体素浮空宝塔\n\n精致的细节，到了疯狂的地步\n\n这种体素宝塔感觉已经完全体现不了 Fable 5.2的能力上限了。。",
        partial=True,
    ),
    dict(
        slug="leo114119-673746", author="leo114119", name="Leo · Building w/ AI",
        status="2119928576548237346",
        title="Thousands of 3D pelicans riding around an island",
        category="3d", tech=["3D", "pelican", "pure-code"],
        prompt="Fable 5.2 用代码生成的动漫 3D 鹈鹕骑行岛\n这一次不用一个一个的画了，直接给你成千上万的鹈鹕，喜欢哪个看哪个吧：",
        partial=True,
    ),
    dict(
        slug="duoyun-77-045860", author="duoyun_77", name="多云",
        status="2120026864333045860",
        title="A whole replicated Earth — weather synced with the real planet",
        category="3d", tech=["3D", "earth", "interactive"],
        prompt="Fable 5.2 “复制”了一整个地球 🌍\n\n想去哪就去哪\n想拆就拆\n据说天气还跟真实地球同步 😱",
        partial=True,
    ),
    dict(
        slug="khvostikk-889130", author="KHvostikk", name="Konstantin Zolozhkov",
        status="2119939061049889130",
        title="Fable 5.2 video-to-3D animation",
        category="3d", tech=["3D"],
        prompt="Fable 5.2 video to 3d animation",
        partial=True,
    ),
    dict(
        slug="seiiiiiiiiiiru-747313", author="seiiiiiiiiiiru", name="SEIIIRU😈AIを使う映像クリエイター",
        status="2119919169768747313",
        title="Fable 5.2 driving Blender like a pro",
        category="3d", tech=["Blender"],
        prompt="Claude Fable 5.2\nBlender操作やっべーんやけどｗ",
        partial=True,
    ),
    dict(
        slug="jamesda-259589", author="JamesDa55049936", name="路遥",
        status="2120028680026259589",
        title="Movie-grade effects straight out of Fable 5.2",
        category="3d", tech=["3D", "cinematic"],
        prompt="这fable 5.2 成精了吧，做的效果和电影效果一样了！！！ claude 你这是想要把电影演员们打失业啊！！！ 太卷了。",
        partial=True, likes=6, views=424, duration="0:30",
    ),

    # ------------------------------------------------------ Motion graphics
    dict(
        slug="khazix0918-590834", author="Khazix0918", name="数字生命卡兹克",
        status="2119902325460590834",
        title="A 4th-birthday video for ChatGPT — made with Claude Fable 5.2",
        category="motion", tech=["motion-graphics", "music-video"],
        prompt="Claude Fable 5.2的视频能力又大幅进化了，节奏和动效太强了...强的有点过于离谱了。 ChatGPT就要四周年了，我用Claude Fable 5.2给ChatGPT四周年提前做了一个庆生视频，这个细节这个节奏，强无敌。。。 只能说，愿Claude和GPT继续相爱相杀...",
        partial=True, likes=460, views=56342, duration="0:58",
    ),
    dict(
        slug="mattshumer-892403", author="mattshumer_", name="Matt Shumer",
        status="2119884041331892403",
        title="Fable 5.2 ONE-SHOTTED this video ('makes Opus look like a toy')",
        category="motion", tech=["pure-code", "one-shot"],
        prompt="Fable 5.2 ONE-SHOTTED this video. It makes Opus look like a toy.",
        partial=True, likes=687, views=161298, duration="4:41",
        note="Full video linked from the post on YouTube.",
    ),
    dict(
        slug="mattshumer-828670", author="mattshumer_", name="Matt Shumer",
        status="2119900920347828670",
        title="An entire movie in pure code — voices, graphics, everything",
        category="motion", tech=["pure-code", "voice", "music"],
        prompt="Fable 5.2 made this entire movie in pure code.\n\nVoices, graphics, everything.",
        partial=True,
    ),
    dict(
        slug="anabology-457643", author="anabology", name="anabology",
        status="2120010995309457643",
        title="'Make the video of your dreams' — a two-shot, 9-hour, 4-minute film",
        category="motion", tech=["pure-code", "long-form"],
        prompt="Make the video of your dreams.\n\n(Two shots, ~9 hours of autonomous work.)",
        partial=False, likes=673, views=34221, duration="4:02",
        note="Creator's words: 'This was not a one-shot. It was a two-shot. I told Fable 5.2 to make the video of its dreams, and 9 hours later:'",
    ),
    dict(
        slug="suna-gaku-697063", author="suna_gaku", name="スナガク",
        status="2119952985933697063",
        title="'Show me the strongest video that shows off your current abilities'",
        category="motion", tech=["pure-code", "music", "one-shot"],
        prompt="今の実力を見せつける最強の動画を見せて\n\n(Show me the strongest video that shows off your current capabilities. It started by composing the music itself.)",
        partial=False, likes=2663, views=330352, duration="1:26",
    ),
    dict(
        slug="developedbyed-983634", author="developedbyed", name="Dev Ed",
        status="2119898145777983634",
        title="Opus 5.5 (top) vs Fable 5.2 (bottom) — same scene",
        category="motion", tech=["comparison"],
        prompt="Opus 5.5 (top) vs Fable 5.2 (bottom)\n\nReally impressed with Fable 5.2s variety and understanding of the scene",
        partial=True, likes=799, views=43111, duration="0:12",
    ),
    dict(
        slug="ivanainai-397550", author="ivanainai", name="Ivana",
        status="2119915243321397550",
        title="Fable 5.2 vs Opus 5.5 — vibe coding is coming for engineering",
        category="motion", tech=["comparison", "vibe-coding"],
        prompt="Fable 5.2 vs Opus 5.5 Vibe coding is coming for engineering 😨",
        partial=True, likes=428, views=31333, duration="1:52",
    ),
    dict(
        slug="gregoirechp-707355", author="Gregoirechp", name="Gregoire Chapelon",
        status="2119879667457073355",
        title="A complete motion design in a few minutes",
        category="motion", tech=["motion-graphics"],
        prompt="FABLE 5.2 just came out, and it made a motion design in a few minutes. It's completely WTF",
        partial=True, likes=309, views=18052, duration="0:40",
    ),
    dict(
        slug="devsvn2-070289", author="devsvn2", name="Adi",
        status="2119875516216070289",
        title="Fable 5.2 one-shotted this",
        category="motion", tech=["one-shot"],
        prompt="Fable 5.2 one shotted this btw",
        partial=True, likes=222, views=54448, duration="0:35",
    ),
    dict(
        slug="dfeinition-859818", author="dfeinition", name="Dan Fein",
        status="2119881243990859818",
        title="Chalk art brought to life",
        category="motion", tech=["chalk", "style"],
        prompt="Fable 5.2 brought some chalk art to life",
        partial=True, likes=168, views=6148, duration="0:31",
    ),
    dict(
        slug="seanaiux-505512", author="seanaiux", name="Sean Galt",
        status="2119888254753505512",
        title="Crazy pixel-style aquarium toggle switch",
        category="motion", tech=["pixel-art", "CSS", "UI"],
        prompt="Free prompt published by the author at: https://uberdesigner.ai/t/aquarium-tog",
        partial=True, likes=145, views=6104, duration="0:12",
        note="The creator shared the prompt for free on his own site (linked above).",
    ),
    dict(
        slug="leviwoyun-258308", author="Leviwoyun", name="Levi 卧云",
        status="2119955625820258308",
        title="A 30-second motion-graphics portfolio reel, produced in 24 minutes",
        category="motion", tech=["motion-graphics", "music"],
        prompt="制作一段 30 秒动态图形短片，展现作为动态设计师出众的实力，就当做用于简历的个人作品集，请尽情发挥",
        partial=False,
        note="Creator: '已被 Fable 5.2 大人吓哭，前端设计这块遥遥领先！视频动效+配乐，24 分钟生产，动态设计师要学多少年？'",
    ),
    dict(
        slug="leviwoyun-037492", author="Leviwoyun", name="Levi 卧云",
        status="2120053612131037492",
        title="A cosmic black-hole switch",
        category="motion", tech=["3D", "UI"],
        prompt="用 Fable 5.2 做一个宇宙黑洞开关",
        partial=True, likes=17, views=840, duration="0:18",
    ),
    dict(
        slug="gkev1n-617868", author="GKev1n", name="gKev1n",
        status="2119923603785617868",
        title="The pelican test — the most perfect pelican-on-a-bicycle SVG animation ($4, 10 min)",
        category="motion", tech=["SVG", "pelican"],
        prompt="震惊！！瘫坐！！ 这是 Fable 5.2 的鹈鹕测试！！这也太牛逼了吧？？感觉这是我见过最完美的鹈鹕骑单车 svg 动画了！！ 所有的细节没有任何问题！ Made With Fable 5.2 middle，10 分钟，花费 4 $！！Claude Pro Fable 专属额度花费 5%",
        partial=True, likes=17, views=8055, duration="0:10",
    ),
    dict(
        slug="leo114119-807264", author="leo114119", name="Leo · Building w/ AI",
        status="2119943368079802645",
        title="MAX pelican-on-a-bicycle SVG test — natural and smooth",
        category="motion", tech=["SVG", "pelican"],
        prompt="创建一个Html文件，使用svg 绘制一只鹈鹕骑自行车的动画",
        partial=False,
        note="Creator's verdict: '返朴归真，很自然流畅，但没有之前那些惊艳的拟真细节' (prompt via B站).",
    ),
    dict(
        slug="leo114119-630075", author="leo114119", name="Leo · Building w/ AI",
        status="2119989377132630075",
        title="A peacock riding a bicycle — and it even displays its tail",
        category="motion", tech=["SVG", "peacock"],
        prompt="Claude Fable 5.2生成的孔雀骑车 SVG 动画\n\n孔雀还会开屏，这你受得了吗？",
        partial=True,
    ),
    dict(
        slug="leo114119-037293", author="leo114119", name="Leo · Building w/ AI",
        status="2119945755100373293",
        title="Pelican-ception: a bicycle riding a pelican riding a bicycle",
        category="motion", tech=["SVG", "pelican", "recursion"],
        prompt="Fable 5.2 经典项目 ：\n\n骑自行车的控制器骑着骑鹈鹕的自行车骑着骑自行车的鹈鹕\n\n动画细节的刻画更细了：还多了一些喂食的小动画\n\n老实说 对于Fable 5.2，这种动画测试已经完全没有难度",
        partial=True,
    ),
    dict(
        slug="aziz4ai-200726", author="aziz4ai", name="AZIZ | AI 🇸🇦",
        status="2119928581405200726",
        title="A 15-second motion scene, no video model — code only (4% of weekly quota)",
        category="motion", tech=["pure-code", "motion-graphics"],
        prompt="الموشن جرافيك رايح لبعد اخر 😱\n\nجربت اطلب من Fable 5.2 يسوي لي مشهد مدته ١٥ ثانية بدون اي نموذج فيديو .. بس بالكود\n\nنتيجة حرقت ٤٪ من حدي الاسبوعي بس احسها تستاهل وشرايكم 🤫",
        partial=True, duration="0:15",
    ),
    dict(
        slug="ohayou792-587380", author="ohayou792", name="Unicorn",
        status="2119994876926587380",
        title="3D flip-book animation — $15.77 and 21 minutes",
        category="motion", tech=["3D", "flip-book"],
        prompt="不让Fable 5.2写代码反而又快又省。\n\n做一套 3D 翻页书动画，让 Fable 5.2 自己去写，跑了 21 分钟，花费了 15.77 刀。中途有一次因为单条回复太长，超出 128k 上下文长度直接中断，单次就浪费了 5.5 刀。",
        partial=True,
    ),
    dict(
        slug="freedomaig-763821", author="FreedomAIG", name="Freedom | AI",
        status="2120017167848763821",
        title="Ink-wash animation: Fable 5.2 vs his earlier Opus 5.5 version",
        category="motion", tech=["ink-wash", "comparison"],
        prompt="同样是 Claude做的动态效果，下面是用Fable 5.2做的，引用对比的是我之前Opus 5.5做的，这个差别实际很直观了。",
        partial=True, likes=3, views=594, duration="0:15",
    ),
    dict(
        slug="amihai-205099", author="amihai", name="Amichai Mantinband",
        status="2119894821255205099",
        title="'Go wild on the canvas' — no prompt, and oh boy",
        category="motion", tech=["Canvas"],
        prompt="go wild on the canvas",
        partial=False,
        note="Creator: 'no prompt, just told fable 5.2 to go wild on the canvas... OH BOY 🧵' (thread).",
    ),
    dict(
        slug="fuxun233-052799", author="fuxun233", name="Nori",
        status="2120053721573052799",
        title="Signature Claude aesthetics",
        category="motion", tech=["aesthetics"],
        prompt="Fable 5.2的作品，claude的审美一如既往的安心\n\n这是GPT一辈子都做不出来的内容",
        partial=True,
    ),
    dict(
        slug="xkaka1456-717666", author="xKaka1456", name="卡卡",
        status="2120008408774717666",
        title="Fable 5.2 interprets aesthetics",
        category="motion", tech=["aesthetics"],
        prompt="Fable 5.2 诠释审美\n\n说真的，三年前你要跟我说 AI 能做出这种效果，我肯定会笑你异想天开…\n\n但现在，一切皆有可能。",
        partial=True,
    ),
    dict(
        slug="fiapp-pro-585134", author="fiapp_pro", name="索螺丝",
        status="2119998595059585134",
        title="A video made with Claude Fable 5.2 — 'just insane'",
        category="motion", tech=["motion-graphics"],
        prompt="claude fable 5.2 做的视频，也太牛逼了！",
        partial=True, likes=13, views=7184, duration="0:39",
    ),
    dict(
        slug="lovekeshanand07-613199", author="LovekeshAnand07", name="Lovekesh Anand",
        status="2120024384685613199",
        title="A launch video from a single prompt",
        category="motion", tech=["launch-video", "one-shot"],
        prompt="Fable 5.2 made this launch video with a single prompt",
        partial=True,
    ),
    dict(
        slug="devteamdrew-241283", author="devteamdrew", name="DreW",
        status="2119892540950241283",
        title="Made with Claude Fable 5.2",
        category="motion", tech=["motion-graphics"],
        prompt="Made with @claudeai Fable 5.2",
        partial=True,
    ),
    dict(
        slug="vibe-walking-842784", author="vibe_walking", name="りも(Limo)",
        status="2119994132269842784",
        title="'Fable 5.2? Make me something!' — a homepage background animation",
        category="motion", tech=["background", "web"],
        prompt="わい「Fable 5.2？なんか作ってー！」\n\nClaude「ほい」\n\n普通にホームページの後ろにあったらかっこよさそう",
        partial=True,
    ),
    dict(
        slug="qwjcool-393425", author="qwjcool", name="robert.qiu",
        status="2120051782009393425",
        title="The most beautiful flora & fauna world, with self-composed music",
        category="motion", tech=["nature", "music"],
        prompt="请你想象一下最美的动植物世界景象，再配上最合适的音乐，制作一段一分钟以内的视频",
        partial=False,
        note="Made with Fable 5.2 (creator wrote 'Fable 5.5 medium' — the Claude middle tier). Claude '<没有废话，直接开干了>'.",
    ),
    dict(
        slug="wshuyi-417720", author="wshuyi", name="Wang Shuyi",
        status="2120014892040417720",
        title="Saber-tooth tiger hunt — pure-code animation with self-generated SFX",
        category="motion", tech=["pure-code", "sfx", "no-skills"],
        prompt="不使用任何技能，做一段纯编程形成的动画视频：剑齿虎的捕猎。不用配音，你自己编程生成音效，时长控制在 30 秒以内",
        partial=False, likes=7, views=2671, duration="0:20",
    ),
    dict(
        slug="akokoi1-491817", author="akokoi1", name="WY",
        status="2119986791474491817",
        title="A 60-second one-shot ride through human art history",
        category="motion", tech=["art-history", "one-shot"],
        prompt="做一个60秒的短片，展示人类艺术史，要求做到引人入胜，一镜到底。",
        partial=False,
        note="Creator: 'Fable 5.2，一句提示词出的视频！比Opus5.5的审美又提升了不少。'",
    ),
    dict(
        slug="miyataarchack-529420", author="miyataArcHack", name="宮田 |Cloudflare x ClaudeCode",
        status="2120066807088529420",
        title="Battle animation (~10% of the weekly quota)",
        category="motion", tech=["battle", "animation"],
        prompt="Fable 5.2で戦闘アニメーションを作ってみた。 使用量は大体週間制限の10%くらい。",
        partial=True, duration="0:34", views=12,
    ),
    dict(
        slug="rjsonha-574444", author="RJasonHA", name="Fries",
        status="2120041766363574444",
        title="A cinematic stickman fight",
        category="motion", tech=["stickman", "fight", "physics"],
        prompt="电影级别制作的火柴人！！！ 🤣🤣 Fable 5.2已经完全具备制作火柴人电影的能力了，这个打斗和特效，感觉从制作逻辑上，代码制作有更严谨碰撞效果。",
        partial=True, likes=10, views=387, duration="0:15",
    ),
    dict(
        slug="yuziyyaa-471752", author="Yuziyyaa", name="Youzi",
        status="2120031965034471752",
        title="Stickman test — Fable 5.2 ($40) vs Opus 5.5 ($18)",
        category="motion", tech=["stickman", "comparison"],
        prompt="Fable 5.2这波Stickman测试简直夸张\n华丽的动作编排+慢动作镜头，已经把动画质量拉到离谱级别了！！\n\nFable 5.2 花费40💵Opus5.5  花费18💵\n用时上面Fable 5.2领先一分钟完成\n\n虽然花费更多，但是动作和效果上确实更值得回票！",
        partial=True,
    ),
    dict(
        slug="eianlu-409493", author="EianLu", name="Eian",
        status="2120052032157409493",
        title="Re-creating the official launch video — 90% identical",
        category="motion", tech=["replication", "comparison"],
        prompt="测试了一下Fable 5.2能力，让它比着官方宣传片自己复刻一个视频出来。 跑了一个小时给了我这个，和原片比对了一下，不敢说100%一致，90%是有的，再多优化几轮做到完美不难（为了区分我让它在视频开头的小人背上插了个小旗 😂 ）",
        partial=True, likes=11, views=1433, duration="0:19",
    ),
    dict(
        slug="mathiaschpl-676283", author="mathiaschpl", name="Mathias Chapelon",
        status="2119878412181676283",
        title="Fable 5.2 did this in 10 minutes",
        category="motion", tech=["motion-graphics", "fast"],
        prompt="Fable 5.2 did this in 10 minutes 😳\n\nthis is insanee",
        partial=True,
        note="Re-shared by @guanmo_ai ('Fable 5.2 10分钟做到这个程度？').",
    ),
    dict(
        slug="hello-amani-837842", author="hello_amani", name="Amani • Design Partner",
        status="2119873980786237842",
        title="Animation & 3D experiments that keep you experimenting",
        category="motion", tech=["3D", "animation"],
        prompt="omg, claude fable 5.2 is seriously good at animation and 3D\n\nthis is the kind of output that keeps me experimenting",
        partial=True,
    ),
    dict(
        slug="berryxia-089168", author="berryxia", name="Berryxia.AI",
        status="2119947402107089168",
        title="A desktop-tidying robot animation, iterated over a few chats",
        category="motion", tech=["robot", "iteration"],
        prompt="我去，Fable 5.2 简直太神了！ ！！ 分分钟给你搓出你想要的一切啊！ 早起后，看到Fable 5.2发布，迫不及待找点活干！ 正好前几天在视频号刷到一个博主做的类似桌面整理文件的扫地机器人形式，我也想自己做一下，于是用fable 5.2 对话了几轮，按照要求迭代了一下，他直接实现了我的对应想法。",
        partial=True, likes=31, views=2973, duration="1:26",
    ),
    dict(
        slug="yihui-indie-175762", author="yihui_indie", name="Yihui",
        status="2119964172171755762",
        title="The Fable 5.2 launch-video style, distilled into a reusable Skill",
        category="motion", tech=["Skill", "4K", "launch-video"],
        prompt="Fable 5.2 的 launch video 太优雅了。\n\n我让 Fable 5.2 自己把这个风格做成了 Skill：一条弧形的地平线，一个小人从左走到右，25 种场景可以随意组合。给它产品名和 Logo，就能出一支你自己的 4K 发布片。\n\nSkillry 上所有的 Skill 都已经兼容 Fable 5.2。",
        partial=True,
        note="Meta-entry: the launch-video style as a reusable Skill on Skillry (25 mix-and-match scenes; product name + logo in, 4K launch film out).",
    ),
    dict(
        slug="karminski3-534965", author="karminski3", name="karminski-牙医",
        status="2120007187808534965",
        title="Same demo: Fable 5.2 ($40) vs DeepSeek v4.1 Flash (¥1.4)",
        category="motion", tech=["comparison"],
        prompt="Fable-5.2 刚刚发布, 给大家做一个小 demo 看下效果, 上面这个是 deepseek-v4.1-flash-1017 生成的, 花费1块4毛. 下面是 Fable-5.2 生成的, 花费40刀😇. 大家看看值吗?",
        partial=True, likes=65, views=13169, duration="0:59",
    ),

    # --------------------------------------------------- Games & interactive
    dict(
        slug="felixrieseberg-463609", author="felixrieseberg", name="Felix Rieseberg",
        status="2119925633564463609",
        title="One-shot AAA web game — every model, sound and texture from scratch ($550, 8 h)",
        category="games", tech=["game", "FPS", "playable", "one-shot"],
        prompt="I wanted to test Fable 5.2's quality with one-shot prompts without human feedback. Everything in this game is from scratch: models, sounds, textures. ~$550 at API pricing, ~2.7M output and 445M input tokens, heavily cached. Took 8 hours! Play it here: claude.ai/artifact/BGY1S",
        partial=True, likes=5537, views=713808, duration="1:12",
        note=("By an Anthropic engineer. Playable artifact — the viral 'AAA-level' post @TokenGremlin "
              "(8,988 likes, 822K views) shared this build. He made two more games the same way "
              "(see also claude.ai/artifact/MXxb3)."),
    ),
    dict(
        slug="fly3nn-715156", author="fly3nn", name="Flynn",
        status="2119974687157715156",
        title="An Attack on Titan game from a single sentence",
        category="games", tech=["game", "one-shot"],
        prompt="生成一个进击的巨人游戏",
        partial=False, likes=1, views=1620, duration="1:36",
        note="Creator: 'fable 5.2 一句话生成的游戏，我认为这已经完美展现了fable5.2的能力了！'",
    ),
    dict(
        slug="stargridcompass-529138", author="Stargridcompass", name="高运通",
        status="2119989441322529138",
        title="Racing mini-game — drift feel, nitro boost, wall feedback (same prompt as GPT-6.2 Sol)",
        category="games", tech=["game", "racing", "comparison"],
        prompt="今天用同样的提示词，让 Fable 5.2 做了个赛车小游戏。 漂移手感、氮气加速、撞墙反馈，细节做得相当到位，整体效果远超预期。 昨天还在夸GPT-6.2 Sol性价比无敌，结果只领先了半天，就被Fable 5.2反超了。",
        partial=True, likes=13, views=1368, duration="0:55",
    ),
    dict(
        slug="aiwaremax-701089", author="aiwaremax", name="AIWare",
        status="2119942626325701089",
        title="A Zelda-like world re-created — modeling, shadows, ambient light",
        category="games", tech=["game", "zelda", "3D"],
        prompt="游戏和视频行业又一次被震惊到了吗 Claude Fable 5.2 再造了一个塞尔达传说 人物建模、动作影子、环境光效 不标注，这TM谁知道是AI生成的啊",
        partial=True, views=88, duration="0:25",
    ),
    dict(
        slug="leo114119-223795", author="leo114119", name="Leo · Building w/ AI",
        status="2119999332682223795",
        title="One-click remake of NetEase's 'Eggy Party'",
        category="games", tech=["game", "remake"],
        prompt="Fable 5.2 一键复刻“蛋仔派对”小游戏 这大模型要早点放出来，都没网易什么事了。。",
        partial=True, likes=11, views=1104, duration="0:47",
    ),
    dict(
        slug="futurestacked-221889", author="FutureStacked", name="Future Stacked",
        status="2120066532856221889",
        title="The iPhone Duo becomes a holographic projector",
        category="games", tech=["interactive", "demo", "hardware-concept"],
        prompt="The iPhone Duo becomes a holographic projector in this demo built with Claude Fable 5.2.",
        partial=True, likes=2, views=233, duration="0:18",
    ),

    # ------------------------------------------------------------ Explainers
    dict(
        slug="diegocabezas01-866912", author="diegocabezas01", name="Diego | AI 🚀 - e/acc",
        status="2119978348440866912",
        title="How a traffic light works — one-way street simulation in Python",
        category="explainer", tech=["Python", "simulation"],
        prompt="write a python code that visualizes how a traffic light works in a one way street with cars entering at random rate",
        partial=False,
        note="Run on 'Claude Fable 5.2 High'.",
    ),
    dict(
        slug="linxiaobei888-829227", author="linxiaobei888", name="小北AI",
        status="2119978892861829227",
        title="An English-learning animation episode for 3–6 year olds",
        category="explainer", tech=["education", "kids", "animation"],
        prompt="Claude Fable 5.2 做的英语启蒙视频太棒了！\n\n最近我儿子在上英语课，老师给了几个视频让他在家看，但是我觉得太一般了，而且不够有趣，娃也不爱看\n\n于是我就想，这种视频 Claude 应该很擅长才对啊，立马安排，做了一集给 3-6 岁孩子看的英语启蒙动画\n\n句型、选画风，教哪些词、笑点放哪全部都是…",
        partial=True,
    ),
    dict(
        slug="egichzz-200515", author="Egichzz", name="Egich.",
        status="2120067587606200515",
        title="A Beethoven-style piano sonata in LilyPond — sheet music, audio and a video of every note",
        category="explainer", tech=["LilyPond", "music", "notation"],
        prompt="someone asked it to compose a movement in LilyPond, and it reportedly generated sheet music, audio and even a video showing every note",
        partial=True, duration="1:28",
        note="News-style post about the capability; includes the generated play-along video.",
    ),
]

ADDED = "2026-11-10"


def post_url(e):
    return "https://x.com/%s/status/%s" % (e["author"], e["status"])


def author_url(e):
    return "https://x.com/%s" % e["author"]


def fmt_count(n):
    if n is None:
        return None
    if n >= 1000000:
        return "%.1fM" % (n / 1000000.0)
    if n >= 1000:
        return "%.1fK" % (n / 1000.0)
    return str(n)


def existing_posters():
    """Poster paths fetched by tools/fetch_posters.py, keyed by slug, so a
    rebuild does not lose them."""
    path = os.path.join(ROOT, "data", "videos.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return {v["slug"]: v["poster"] for v in json.load(f) if v.get("poster")}
    except Exception:
        return {}


def build_videos_json():
    posters = existing_posters()
    out = []
    for e in ENTRIES:
        v = {
            "slug": e["slug"],
            "author": e["author"],
            "author_url": author_url(e),
            "post_url": post_url(e),
            "title": e["title"],
            "category": e["category"],
            "tech_tags": e["tech"],
            "prompt": e["prompt"],
            "prompt_partial": e["partial"],
            "added": ADDED,
        }
        if e["slug"] in posters:
            v["poster"] = posters[e["slug"]]
        if e.get("likes") is not None:
            v["likes"] = e["likes"]
        if e.get("views") is not None:
            v["views"] = e["views"]
        if e.get("duration"):
            v["duration"] = e["duration"]
        if e.get("note"):
            v["notes"] = e["note"]
        out.append(v)
    path = os.path.join(ROOT, "data", "videos.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return len(out)


def build_prompt_files():
    d = os.path.join(ROOT, "prompts")
    os.makedirs(d, exist_ok=True)
    for e in ENTRIES:
        lines = []
        lines.append("# Fable 5.2 video by @%s" % e["author"])
        lines.append("")
        lines.append("[Original post](%s)" % post_url(e))
        lines.append("")
        lines.append("- **Category:** %s" % CATEGORIES[e["category"]])
        if e["tech"]:
            lines.append("- **Built with:** %s" % " · ".join(e["tech"]))
        lines.append("- **Author:** [@%s](%s)" % (e["author"], author_url(e)))
        if e.get("duration"):
            lines.append("- **Video length:** %s" % e["duration"])
        if e.get("likes") is not None or e.get("views") is not None:
            eng = []
            if e.get("likes") is not None:
                eng.append("%s likes" % fmt_count(e["likes"]))
            if e.get("views") is not None:
                eng.append("%s views" % fmt_count(e["views"]))
            lines.append("- **Engagement when collected (2026-11-10):** %s" % " · ".join(eng))
        if e.get("note"):
            lines.append("")
            lines.append("> %s" % e["note"].replace("\n", "\n> "))
        lines.append("")
        if e["partial"]:
            lines.append("## Original post")
            lines.append("")
            lines.append("No standalone prompt was published — this is the creator's original post:")
            lines.append("")
        else:
            lines.append("## Prompt")
            lines.append("")
        lines.append("```text")
        lines.append(e["prompt"])
        lines.append("```")
        lines.append("")
        with open(os.path.join(d, "%s.md" % e["slug"]), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))
    return len(ENTRIES)


def table_rows(entries, posters):
    """Reference-style HTML table: 3 preview cards per row."""
    cells = []
    for e in entries:
        alt = "Fable 5.2 video by @%s" % e["author"]
        poster = posters.get(e["slug"])
        if poster:
            media = '<a href="%s"><img src="%s" alt="%s" width="100%%"></a>' % (
                post_url(e), poster, alt.replace('"', ""))
        else:
            media = '<a href="%s"><b>%s</b></a>' % (post_url(e), e["title"])
        cell = (
            '<td width="33%%" valign="top">%s<br>'
            '<a href="%s"><b>@%s</b></a> \u00b7 <a href="prompts/%s.md">Prompt</a><br>'
            "<sub>%s</sub></td>"
            % (media, post_url(e), e["author"], e["slug"], " \u00b7 ".join(e["tech"]))
        )
        cells.append(cell)
    rows = []
    for i in range(0, len(cells), 3):
        rows.append("<tr>" + "".join(cells[i:i + 3]) + "</tr>")
    return ["<table>"] + rows + ["</table>"]


def build_readme():
    by_cat = {}
    for e in ENTRIES:
        by_cat.setdefault(e["category"], []).append(e)
    order = ["official", "motion", "3d", "games", "explainer"]
    posters = existing_posters()

    L = []
    L.append("# Awesome Fable 5.2 Videos")
    L.append("")
    L.append("Videos, motion graphics, 3D scenes and games people made with **Claude Fable 5.2** "
             "in the first ~48 hours after launch — each with the prompt the creator shared "
             "(or, where no prompt was published, their original post).")
    L.append("")
    L.append("Almost every video here was made by asking Fable 5.2 to produce the animation as "
             "*code* (Blender Python, HTML, Canvas, SVG, Three.js and friends) — no video "
             "model involved. Pick one, copy its prompt, and try it with your own agent.")
    L.append("")
    n_prompts = sum(1 for e in ENTRIES if not e["partial"])
    L.append("- %d posts curated from X in [`data/videos.json`](data/videos.json), each with a page in [`prompts/`](prompts/)" % len(ENTRIES))
    L.append("- Video cover images included in [`assets/posters/`](assets/posters/)")
    L.append("- %d of them include the creator's actual prompt, ready to copy" % n_prompts)
    L.append("- Every entry links to the creator's original post")
    L.append("- Latest update (2026-11-10): first collection, gathered on launch day")
    L.append("")
    L.append("## Contents")
    L.append("")
    for c in order:
        if c in by_cat:
            anchor = CATEGORIES[c].lower().replace(" & ", "--").replace(" ", "-")
            L.append("- [%s](#%s) (%d)" % (CATEGORIES[c], anchor, len(by_cat[c])))
    L.append("- [How to use a prompt](#how-to-use-a-prompt)")
    L.append("- [Credits](#credits)")
    L.append("")
    for c in order:
        if c not in by_cat:
            continue
        L.append("## %s" % CATEGORIES[c])
        L.append("")
        L.extend(table_rows(by_cat[c], posters))
        L.append("")
    L.append("## How to use a prompt")
    L.append("")
    L.append("1. Open a prompt page from the table above (or browse [`prompts/`](prompts/)).")
    L.append("2. Paste the prompt into Claude with the Fable 5.2 model selected.")
    L.append("3. Let it write and run the code — Blender Python, an HTML file, an SVG "
             "animation… — then iterate in plain language (`slower camera`, "
             "`more particles`, `loop it`).")
    L.append("")
    L.append("Prompts marked with a full **Prompt** section are verbatim from the creator; "
             "entries showing **Original post** did not publish a reusable prompt, so the post "
             "itself is the best available starting point.")
    L.append("")
    L.append("## Credits")
    L.append("")
    L.append("Every video belongs to its creator — follow the links in the tables and show "
             "them some love. Special thanks to:")
    L.append("")
    L.append("- [@rileybrown](https://x.com/rileybrown) for the one-prompt 4K Clawd short and "
             "its full prompt, and [@JamesDa55049936](https://x.com/JamesDa55049936) for "
             "publishing the prompt in full")
    L.append("- [@felixrieseberg](https://x.com/felixrieseberg) (Anthropic) for the one-shot "
             "AAA web game stress test")
    L.append("- [@LexnLin](https://x.com/LexnLin) for the launch-day viral 3D scene")
    L.append("- Anthropic / [@claudeai](https://x.com/claudeai) for Fable 5.2")
    L.append("")
    L.append("Collected from public posts on X on 2026-11-10, the day Claude Fable 5.2 launched. "
             "Engagement numbers are snapshots from collection time.")
    L.append("")
    L.append("Inspired by [awesome-opus5-5-videos](../awesome-opus5-5-videos) — same idea, "
             "one model generation later.")
    L.append("")
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    n1 = build_videos_json()
    n2 = build_prompt_files()
    build_readme()
    print("videos.json: %d entries" % n1)
    print("prompt files: %d" % n2)
    print("README.md written")
