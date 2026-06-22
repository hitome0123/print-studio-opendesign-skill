# Print Studio Operator Guide

## What This Skill Sells

客户给图，印刷厂选规格，Codex 快速生成：

- 客户预览图
- 印刷版文件
- 白底产品图
- 氛围产品图
- QC 报告
- 打包交付 zip

一句话话术：

> 客户给一组图，我们 5-30 分钟出可确认的系列打样包。尺寸、纸张、出血、安全边距、预览图和印刷文件一起生成。

## MVP Products

Start with:

- 贺卡 / greeting card
- 明信片 / postcard
- 桌历或日历卡 / desk calendar card
- 挂历 / wall calendar
- 卡牌套装 / card set
- 书签 / bookmark
- 感谢卡 / thank-you card
- 邀请卡 / invitation card
- 包装插卡 / packaging insert
- 礼品吊牌 / gift tag

## Series Types

- `monthly_calendar`: 12 个月真实日期
- `quarterly`: 4 个季度
- `seasonal`: 春夏秋冬
- `festival_set`: 节日套装
- `custom_cards`: 自定义 N 张标题卡

V1 engine fully supports `monthly_calendar`. Other series types should be treated as planned templates unless explicitly implemented.

## Acceptance Standards

- Print files are 300dpi.
- Bleed and safe margin are applied.
- QC report has no FAIL.
- The chosen paper/material key appears in resolved config.
- Screen, print, and commerce files are separated.
- Mockups match the selected product form closely enough for customer proofing.

## Do Not Include In V1

- CMYK/ICC color management
- ERP integration
- Quote calculation
- Production scheduling
- Multi-user web backend
- Foil/UV/embossing simulation as production-accurate output

These can be Phase 2 paid additions.
