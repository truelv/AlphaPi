# 分析文档

本目录存放**总体性文档**：分析报告、操作指南、经验总结、逆向笔记，以及官方技术手册。

| 文档 | 主题 | 适用对象 |
|---|---|---|
| [`AlphaPi_实机调试指南.md`](<AlphaPi_实机调试指南.md>) | REPL 使用、终端按键、shell 命令对照、传文件与调试流程、踩坑记录 | **两块板通用** |
| [`AlphaPi_循迹小车（COM10）分析报告.md`](<AlphaPi_循迹小车（COM10）分析报告.md>) | COM10 实机取证、启动链、文件系统、N32 协议、API 全集 | 循迹小车 |
| [`AlphaPi_游戏机（COM11）分析报告.md`](<AlphaPi_游戏机（COM11）分析报告.md>) | COM11 实机取证、手柄硬件、控制链路、打砖块游戏实战 | 游戏机 |
| [`AlphaPi_项目分析文档.md`](<AlphaPi_项目分析文档.md>) | 仓库历史固件（2020 版 / v1.0.3）的源码与反汇编分析、手册要点 | 背景资料 |
| [`board_map.md`](board_map.md) | **逆向速查**：总线/引脚映射、I2C 0x20 电机控制器寄存器表、SPI 屏/灯/摇杆引脚 | 开发/移植 |
| [`lessons_learned.md`](lessons_learned.md) | **踩坑与经验总结**（串口/REPL、base64 传输、`.mpy` 反编译、网络遥控、部署）——做新产品的避雷清单 | **强烈建议先读** |
| [`官方技术参考手册.md`](官方技术参考手册.md) | 官方技术参考手册要点摘录（N32 寄存器、音频参数、12864 LCD 子板等） | 查规格 |
| [`AlphaPi_One_技术参考手册_v4.pdf`](AlphaPi_One_技术参考手册_v4.pdf) | 官方技术参考手册原文 | 查规格 |

## 阅读路径

**刚拿到板子，想连上它：**
1. `AlphaPi_实机调试指南.md` §1–§5
2. `lessons_learned.md` §1（板端串口/REPL 的坑）

**想搞清楚硬件 / 移植：**
1. `board_map.md`（引脚与寄存器速查）
2. 对应设备的实机分析报告（循迹小车 / 游戏机）
3. `../firmware/README.md`（固件代际识别）

**想写自己的程序 / 做遥控：**
1. `lessons_learned.md`（尤其 §2 传输、§6 网络遥控、§7 部署）
2. [`../projects/AlphaPiCar/README.md`](../projects/AlphaPiCar/README.md)（完整可复用示例）
3. 对应实机报告的 API 章节

**想研究固件本身：**
1. `AlphaPi_项目分析文档.md`
2. `../firmware/*/disasm/`（反汇编文本）

## 关联目录

| 目录 | 内容 |
|---|---|
| [`../firmware/`](../firmware/) | 各版本固件备份（本文档的数据来源） |
| [`../board_dump/`](../board_dump/) | 从板子上导出的原始文件与分析中间产物 |
| [`../projects/`](../projects/) | 按项目分类的完整工程（板端 + 上位机） |
| [`../tools/`](../tools/) | 串口、REPL、上传、反汇编、部署等工具 |
