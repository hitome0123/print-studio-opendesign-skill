# 模型客户端提示词包

> 用途：当使用者想把图片风格和展示要求自行喂给 Gemini、OpenAI GPT Image、GPT-Image2、即梦等客户端时，先复制这里的提示词。
> 重要边界：这些提示词用于**辅助预览 / 展示图 / 模型效果测试**，不能替代本 Skill 生成的 `print/` 印刷文件。
> 更安全的默认策略：**不要让模型直接处理已经排好的成品卡面**。模型只生成空白白底/空白氛围背景；成品卡片由本 Skill 或设计软件作为独立图层叠加，避免裁切、改字、重排。

---

## 0. 使用前先填的信息

复制提示词前，先把这些信息填好：

```text
产品类型：例如 5×7 贺卡 / 12 月月历卡 / 明信片 / 书签 / 吊牌
尺寸：例如 5×7 英寸
材质：例如 300g 超白白卡纸 / 珠光纸 / 布纹纸 / 蓝芯纸
系列数量：例如 12 张 / 4 张 / 单张
排版方向：例如 插画居中 + 下方标题 / 上方插画 + 下方日期 / 大留白
文字内容：例如月份、标题、副标题、日期、祝福语
风格：例如温柔插画风 / 复古植物志 / 高级留白 / 节日礼品风
必须保留：最终卡面由本 Skill 输出，不交给模型重画
不能发生：让模型裁切成品卡、改字、重排、重画、加多余文字
```

---

## 1. 通用硬限制

不管用哪个模型，都建议把这一段放在提示词最前面：

```text
重要限制：
这是一项印刷品展示背景生成任务，不是重新设计任务。
不要直接生成或重画我的最终卡面。
如果我上传参考图，只能理解风格、材质和氛围，不能复制、裁切、改写或重排卡面内容。

必须做到：
1. 只生成空白展示背景或空白卡片占位场景。
2. 不在卡片占位区域生成任何图案、文字、日期、数字、logo、标签、水印。
3. 不模仿、重画、改写、裁切我的成品卡面。
4. 卡片占位区域要完整、无遮挡、四边清楚，方便后期叠加真实卡面。
5. 道具、阴影、材质和光线可以生成，但不能遮挡卡片占位区域。
6. 如果需要文字，请只用“no text / blank card placeholder”的概念，不要生成实际文字。
7. 最终应像“为真实卡片准备一个干净背景”，而不是“让模型重新做一张卡片”。
```

---

## 2. Gemini 提示词

适合：让 Gemini 先理解图片并给排版建议；如果要生成展示图，只生成空白背景，不处理成品卡面。

### 2.1 图片理解 + 排版建议

```text
请先分析我上传的这组插画/图片，不要直接生成成品。

请从以下角度判断：
1. 图片是横图、竖图还是方图？
2. 主体是否居中？是否容易被裁切？
3. 画面颜色是偏浅、偏深、偏暖还是偏冷？
4. 细节多不多？缩小成印刷品后会不会糊？
5. 是否适合做系列？适合单张、4 张、6 张还是 12 张？
6. 适合做什么产品：贺卡、明信片、月历卡、挂历、书签、吊牌、卡牌套装？
7. 推荐什么尺寸？为什么？
8. 推荐什么材质？为什么？
9. 推荐什么排版？为什么？
10. 推荐什么字体风格？为什么？
11. 有哪些印刷风险？

输出格式：
- 图片判断
- 产品推荐，至少 3 个选项，每个选项说明理由和风险
- 尺寸推荐，说明理由
- 材质推荐，说明理由和不推荐项
- 排版推荐，说明为什么适合这组图
- 字体推荐，说明小字风险
- 印刷注意事项

不要生成最终图片。
不要裁切、改字、重画或重排我的图片。
```

### 2.2 白底图背景 Prompt

```text
重要限制：
这是一项白底展示背景生成任务，不是卡面生成任务。
不要把我上传的卡面放进场景，不要重画卡面。
请只生成一个适合后期叠加真实卡片的空白白底产品背景。

必须做到：
- 画面中只出现空白卡片占位，不出现任何图案、文字、日期、数字。
- 空白卡片占位四边完整可见。
- 不要添加 logo、贴纸、水印、标签或无关文字。
- 不要模仿我的卡面内容。
- 不要生成任何会覆盖卡面的道具。

场景要求：
生成一个干净的白底产品图。
产品是一张 [产品类型]，尺寸为 [尺寸]，材质为 [材质]。
空白卡片占位正面朝向镜头，轻微自然透视即可。
背景为纯白或接近纯白。
光线柔和，有自然阴影。
产品占画面约 70%，周围保留干净留白。

目标是得到一个可合成背景。真实卡面会由后期图层叠加。
```

### 2.3 氛围图背景 Prompt

```text
重要限制：
这是一项氛围展示背景生成任务，不是卡面生成任务。
不要把我上传的卡面放进场景，不要重画卡面。
请只生成一个适合后期叠加真实卡片的空白氛围场景。

必须做到：
- 画面中只出现空白卡片占位，不出现任何图案、文字、日期、数字。
- 空白卡片占位四边完整可见。
- 不要添加 logo、贴纸、水印、标签或无关文字。
- 不要模仿我的卡面内容。
- 道具只能在周围或背景中，不能遮挡卡片占位区域。

场景要求：
生成一个温暖、干净、有纸品质感的桌面场景。
可以有木桌、花、陶瓷杯、布料、笔记本等辅助道具。
道具只能作为背景，不要遮挡空白卡片占位。
空白卡片占位是画面主角，正面大部分朝向镜头。
光线柔和，整体风格为 [风格]。

目标是得到一个可合成背景。真实卡面会由后期图层叠加。
```

---

## 3. OpenAI GPT Image 提示词

适合：生成白底/氛围背景。不要把已经生成好的排版图交给模型改图；真实卡面后期叠加。

### 3.1 白底图

```text
Create a clean white-background product mockup background with a blank card placeholder.

Hard constraints:
- This is a background generation task, not a card design task.
- Do not place, redraw, reinterpret, or edit the final card design.
- The card area must be a blank placeholder only.
- No artwork, text, dates, numbers, logos, labels, stickers, or watermarks on the placeholder.
- The blank placeholder must be fully visible with all four edges shown.
- Do not cover the placeholder with props.

Scene:
Place a blank card placeholder upright in a simple natural wooden stand on a pure white seamless background.
Front-facing ecommerce product photography.
Soft studio lighting.
Clean gentle shadow.
The blank placeholder should fill about 70% of the image with balanced white margin.

Product details:
Product type: [产品类型]
Size: [尺寸]
Material: [材质]
Style: [风格]

The real card design will be composited later as a separate layer. Generate only the clean background and blank placeholder.
```

### 3.2 氛围图

```text
Create a warm lifestyle product mockup background with a blank card placeholder.

Hard constraints:
- This is a background generation task, not a card design task.
- Do not place, redraw, reinterpret, or edit the final card design.
- The card area must be a blank placeholder only.
- No artwork, text, dates, numbers, logos, labels, stickers, or watermarks on the placeholder.
- The blank placeholder must be fully visible with all four edges shown.
- Do not cover the placeholder with props.

Scene:
Place a blank card placeholder upright in a natural wooden stand on a light wooden desk.
Use a cozy warm home interior style.
Soft natural daylight from the side.
The background may include blurred flowers, a ceramic cup, a notebook, or soft fabric as secondary props.
The blank placeholder must remain the clear hero and be large enough for later compositing.
Keep the placeholder front mostly facing the camera, not overly angled.

Product details:
Product type: [产品类型]
Size: [尺寸]
Material: [材质]
Style: [风格]

The real card design will be composited later as a separate layer. Generate only the warm scene and blank placeholder.
```

---

## 4. GPT-Image2 提示词

> 当前项目里 `gpt_image2` 作为 GPT 图像类模型预览位。使用逻辑与 OpenAI GPT Image 类似，但提示词可以更强调“layout lock”。

### 4.1 Layout Lock 白底图

```text
Blank placeholder mockup request.

Do not use the final card design as an editable image.
Generate only a clean product photography background with a blank card placeholder.

Do not:
- create any artwork on the placeholder
- write text or numbers on the placeholder
- imitate the final card design
- add labels, watermarks, stickers, or decorative text
- cover the placeholder with props

The blank placeholder must remain visible, flat, rectangular, and empty.
All four edges must be visible for later compositing.

Create a white-background ecommerce product photo.
The blank card placeholder stands in a simple natural wooden holder.
Pure white seamless background.
Soft even light.
Subtle realistic shadow.
Product fills around 70% of the frame.

Product:
[产品类型], [尺寸], [材质], [风格].
```

### 4.2 Layout Lock 氛围图

```text
Blank placeholder lifestyle mockup request.

Do not use the final card design as an editable image.
Generate only a warm lifestyle background with a blank card placeholder.

Do not:
- create any artwork on the placeholder
- write text or numbers on the placeholder
- imitate the final card design
- add labels, watermarks, stickers, or decorative text
- cover the placeholder with props

The blank placeholder must remain visible, flat, rectangular, and empty.
All four edges must be visible for later compositing.

Create a warm lifestyle product photo.
The blank card placeholder stands in a natural wooden holder on a light wooden desk.
Soft daylight.
Blurred flowers, ceramic cup, notebook, or soft fabric can appear as background props.
Props must not cover the placeholder.
The placeholder is the hero.

Product:
[产品类型], [尺寸], [材质], [风格].
```

---

## 5. 即梦提示词

适合：在即梦客户端里手动测试白底图和氛围图。建议语言更直接，限制写在前面。

### 5.1 即梦白底图

```text
请生成一张白底产品展示背景图，用于后期叠加真实卡面。

重要：这是背景生成，不是卡面生成。
不要把我上传的成品卡面放进画面，不要重画卡面。

严格要求：
1. 画面里只能有空白卡片占位。
2. 空白卡片四条边都要完整出现。
3. 空白卡片上不要有任何图案、文字、日期、数字。
4. 不要模仿我的卡面内容。
5. 不要添加 logo、标签、贴纸、水印或额外文字。
6. 不要让道具遮挡空白卡片。

画面：
一张空白 [产品类型] 占位卡立在简洁自然木质支架上。
纯白背景，电商主图风格。
柔和棚拍光线，自然阴影。
产品占画面约 70%，周围有干净留白。
材质感觉：[材质]。
整体风格：[风格]。

真实卡面会后期叠加到空白卡片区域。
```

### 5.2 即梦氛围图

```text
请生成一张氛围展示背景图，用于后期叠加真实卡面。

重要：这是背景生成，不是卡面生成。
不要把我上传的成品卡面放进画面，不要重画卡面。

严格要求：
1. 画面里只能有空白卡片占位。
2. 空白卡片四条边都要完整出现。
3. 空白卡片上不要有任何图案、文字、日期、数字。
4. 不要模仿我的卡面内容。
5. 不要添加 logo、标签、贴纸、水印或额外文字。
6. 不要让道具遮挡空白卡片。

画面：
把一张空白 [产品类型] 占位卡放在温暖的桌面生活方式场景里。
可以有浅木桌、花、陶瓷杯、笔记本、布料等道具。
道具只能作为背景，不要遮挡空白卡片。
空白卡片是主体，正面朝向镜头，完整可见。
柔和自然光，温暖、高级、干净。
材质感觉：[材质]。
整体风格：[风格]。

真实卡面会后期叠加到空白卡片区域。
```

---

## 6. 给使用者的推荐顺序

建议这样用：

1. 先用本 Skill 的 `advise_project.py` 看图并得到推荐。
2. 用本 Skill 生成 `screen/` 和 `print/`，这是稳定排版来源。
3. 不把 `screen/B_01.jpg` 或 `download_4k/B_01_4k.jpg` 直接交给模型改图。
4. 复制对应模型提示词，只生成空白白底背景或空白氛围背景。
5. 用本 Skill 的 `local_mockup` 或设计软件，把真实卡面作为独立图层叠加到空白占位区域。
6. 如果模型生成的背景遮挡占位区域、占位区域太歪、出现文字或图案，直接丢弃。
7. 最终印刷仍以 `print/` 文件为准。

一句话：

> 模型客户端可以用来生成背景气氛，但不应直接处理成品卡面；成品卡面必须由确定性排版或独立图层合成。
