# 模型客户端提示词包

> 用途：当使用者想把图片和排版要求自行喂给 Gemini、OpenAI GPT Image、GPT-Image2、即梦等客户端时，先复制这里的提示词。  
> 重要边界：这些提示词用于**辅助预览 / 展示图 / 模型效果测试**，不能替代本 Skill 生成的 `print/` 印刷文件。

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
必须保留：原图主体、文字、日期、边距、完整卡面
不能发生：裁切、改字、重排、重画、加多余文字
```

---

## 1. 通用硬限制

不管用哪个模型，都建议把这一段放在提示词最前面：

```text
重要限制：
这是一项印刷品排版/展示预览任务，不是重新设计任务。
请把我上传的图片/卡面当作已经完成的设计稿或核心素材。

必须做到：
1. 不裁切主体。
2. 不自动放大到切边。
3. 不改写任何文字。
4. 不重新生成日期、标题、数字或小字。
5. 不改变原图主体、角色、插画细节和构图关系。
6. 不添加新的 logo、标签、水印、贴纸或无关文字。
7. 不重新设计成另一张图。
8. 如果是 mockup，请保证完整卡片四边都可见。
9. 如果文字太小无法清晰重现，请保持为安静的视觉纹理，不要编造新文字。
10. 最终应像“把现有卡面放进版式/场景”，而不是“根据卡面重新画一张”。
```

---

## 2. Gemini 提示词

适合：让 Gemini 先理解图片，给排版建议，或尝试生成白底/氛围展示图。

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

### 2.2 白底图展示 Prompt

```text
重要限制：
这是一项产品白底展示图任务，不是重新设计任务。
请把我上传的卡面/排版图当作最终成品，只允许把它放进白底产品场景。

必须做到：
- 保留原卡面完整内容。
- 完整卡片四边都必须可见。
- 不裁切卡片。
- 不放大到切掉边缘。
- 不改写任何文字、标题、日期、数字。
- 不改变插画主体、边距、日期网格和排版。
- 不添加新 logo、贴纸、水印或无关文字。
- 不重新设计卡面。

场景要求：
生成一个干净的白底产品图。
产品是一张 [产品类型]，尺寸为 [尺寸]，材质为 [材质]。
卡片正面朝向镜头，轻微自然透视即可。
背景为纯白或接近纯白。
光线柔和，有自然阴影。
产品占画面约 70%，周围保留干净留白。

如果卡面小字无法准确重现，请保持原样作为安静纹理，不要编造新文字。
目标是稳定展示图，不是重新设计图。
```

### 2.3 氛围图展示 Prompt

```text
重要限制：
这是一项氛围展示图任务，不是重新设计任务。
请把我上传的卡面/排版图当作最终成品，只允许把它放进真实场景。

必须做到：
- 完整卡片四边都可见。
- 不裁切卡片。
- 不改写文字、日期、标题、数字。
- 不改变插画主体、边距、日期网格和排版。
- 不重新设计卡面。
- 不添加新 logo、标签、水印或无关文字。

场景要求：
把这张 [产品类型] 放在温暖、干净、有纸品质感的桌面场景中。
可以有木桌、花、陶瓷杯、布料、笔记本等辅助道具。
道具只能作为背景，不要遮挡卡面。
卡片是画面主角，正面大部分朝向镜头。
光线柔和，整体风格为 [风格]。

如果卡面小字无法准确重现，请保持原样作为安静纹理，不要编造新文字。
目标是稳定氛围图，不是重新设计图。
```

---

## 3. OpenAI GPT Image 提示词

适合：把一张已经生成好的排版图作为锚图，生成白底图或氛围图。

### 3.1 白底图

```text
Create a clean white-background product mockup using the attached card image as the exact printed front surface.

Hard constraints:
- This is a mockup task, not a redesign task.
- Treat the attached image as the final printed design.
- Preserve the exact card layout.
- The entire card must be visible with all four edges shown.
- Do not crop the card.
- Do not zoom into the artwork.
- Do not rewrite, replace, regenerate, or distort any text.
- Do not change the title, subtitle, date grid, numbers, margins, illustration, or layout.
- Do not add logos, stickers, labels, watermarks, decorations, or extra text.
- Do not redesign the card.

Scene:
Place the full card upright in a simple natural wooden stand on a pure white seamless background.
Front-facing ecommerce product photography.
Soft studio lighting.
Clean gentle shadow.
The product should fill about 70% of the image with balanced white margin.

Product details:
Product type: [产品类型]
Size: [尺寸]
Material: [材质]
Style: [风格]

If tiny printed text cannot be perfectly reproduced, keep it visually quiet and unchanged rather than inventing new text.
```

### 3.2 氛围图

```text
Create a warm lifestyle product mockup using the attached card image as the exact printed front surface.

Hard constraints:
- This is a mockup task, not a redesign task.
- Treat the attached image as the final printed design.
- Preserve the exact card layout.
- The entire card must be visible with all four edges shown.
- Do not crop the card.
- Do not zoom into the artwork.
- Do not rewrite, replace, regenerate, or distort any text.
- Do not change the title, subtitle, date grid, numbers, margins, illustration, or layout.
- Do not add logos, stickers, labels, watermarks, decorations, or extra text on the card.
- Do not redesign the card.

Scene:
Place the full card upright in a natural wooden stand on a light wooden desk.
Use a cozy warm home interior style.
Soft natural daylight from the side.
The background may include blurred flowers, a ceramic cup, a notebook, or soft fabric as secondary props.
The card must remain the clear hero and be large enough to recognize the design.
Keep the card front mostly facing the camera, not overly angled.

Product details:
Product type: [产品类型]
Size: [尺寸]
Material: [材质]
Style: [风格]

If tiny printed text cannot be perfectly reproduced, keep it visually quiet and unchanged rather than inventing new text.
```

---

## 4. GPT-Image2 提示词

> 当前项目里 `gpt_image2` 作为 GPT 图像类模型预览位。使用逻辑与 OpenAI GPT Image 类似，但提示词可以更强调“layout lock”。

### 4.1 Layout Lock 白底图

```text
Layout lock mockup request.

Use the attached image as a locked final card design.
You may only place the locked card into a clean product photography scene.

Do not:
- crop the card
- change the card aspect ratio
- rewrite any text
- regenerate any date numbers
- alter the illustration
- change the margins
- move layout elements
- add new labels or decorative text
- reinterpret the card design

The full card must remain visible, flat, rectangular, and readable.
All four edges must be visible.

Create a white-background ecommerce product photo.
The card stands in a simple natural wooden holder.
Pure white seamless background.
Soft even light.
Subtle realistic shadow.
Product fills around 70% of the frame.

Product:
[产品类型], [尺寸], [材质], [风格].
```

### 4.2 Layout Lock 氛围图

```text
Layout lock lifestyle mockup request.

Use the attached image as a locked final card design.
You may only place the locked card into a warm lifestyle scene.

Do not:
- crop the card
- change the card aspect ratio
- rewrite any text
- regenerate any date numbers
- alter the illustration
- change the margins
- move layout elements
- add new labels or decorative text
- reinterpret the card design

The full card must remain visible, flat, rectangular, and readable.
All four edges must be visible.

Create a warm lifestyle product photo.
The card stands in a natural wooden holder on a light wooden desk.
Soft daylight.
Blurred flowers, ceramic cup, notebook, or soft fabric can appear as background props.
Props must not cover the card.
The card is the hero.

Product:
[产品类型], [尺寸], [材质], [风格].
```

---

## 5. 即梦提示词

适合：在即梦客户端里手动测试白底图和氛围图。建议语言更直接，限制写在前面。

### 5.1 即梦白底图

```text
请根据我上传的卡面图片生成白底产品展示图。

重要：这是 mockup 展示，不是重新设计。
上传的卡面就是最终设计稿，请完整保留。

严格要求：
1. 卡片四条边都要完整出现。
2. 不要裁切卡片。
3. 不要放大到切掉边缘。
4. 不要改文字。
5. 不要改日期、数字、标题、副标题。
6. 不要改插画主体。
7. 不要改变原始排版、边距和布局。
8. 不要添加 logo、标签、贴纸、水印或额外文字。
9. 不要重新设计成另一张图。

画面：
一张 [产品类型] 立在简洁自然木质支架上。
纯白背景，电商主图风格。
柔和棚拍光线，自然阴影。
产品占画面约 70%，周围有干净留白。
材质感觉：[材质]。
整体风格：[风格]。

如果小字无法清晰还原，请保持原样，不要编造新文字。
```

### 5.2 即梦氛围图

```text
请根据我上传的卡面图片生成氛围展示图。

重要：这是 mockup 展示，不是重新设计。
上传的卡面就是最终设计稿，请完整保留。

严格要求：
1. 卡片四条边都要完整出现。
2. 不要裁切卡片。
3. 不要放大到切掉边缘。
4. 不要改文字。
5. 不要改日期、数字、标题、副标题。
6. 不要改插画主体。
7. 不要改变原始排版、边距和布局。
8. 不要添加 logo、标签、贴纸、水印或额外文字。
9. 不要重新设计成另一张图。

画面：
把这张 [产品类型] 放在温暖的桌面生活方式场景里。
可以有浅木桌、花、陶瓷杯、笔记本、布料等道具。
道具只能作为背景，不要遮挡卡片。
卡片是主体，正面朝向镜头，完整可见。
柔和自然光，温暖、高级、干净。
材质感觉：[材质]。
整体风格：[风格]。

如果小字无法清晰还原，请保持原样，不要编造新文字。
```

---

## 6. 给使用者的推荐顺序

建议这样用：

1. 先用本 Skill 的 `advise_project.py` 看图并得到推荐。
2. 用本 Skill 生成 `screen/` 和 `print/`，这是稳定排版来源。
3. 把 `screen/B_01.jpg` 或 `download_4k/B_01_4k.jpg` 上传到 Gemini / GPT Image / 即梦。
4. 复制对应模型提示词，生成白底图或氛围图。
5. 如果模型结果裁切、改字、重排，直接丢弃。
6. 最终印刷仍以 `print/` 文件为准。

一句话：

> 模型客户端可以用来试展示效果，但不能负责最终排版。

