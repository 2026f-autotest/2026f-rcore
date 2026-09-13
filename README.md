# 2026f rCore 操作系统实验

基于 [LearningOS 2026s rCore 课程模板](https://github.com/LearningOS/2026s-oscamp-professional-2026s-rcore-rCore-Tutorial-Code) 整理，供学员 Fork 到个人 GitHub 账号后完成实验、自动测试，并同步 OpenCamp 成绩。

**课程编号：2073 · 五项实验：每项 100 分 · 总分：500 分**

## 开始实验

1. 在 OpenCamp 加入对应训练营，绑定自己的 GitHub 账号。
2. Fork [本仓库](https://github.com/Alayfolk64/2026f-rcore)，**取消勾选 `Copy the main branch only`**，保留 `main` 和 `ch1` 至 `ch8`。
3. 安装 [GitHub CLI](https://cli.github.com/)，克隆自己的 Fork。
4. 在仓库根目录运行 `python3 setup.py`，按提示登录 GitHub 并粘贴一次课程 Token。脚本自动保存 Secret 并启用 Actions，已有凭证时保留原值。
5. 切换实验分支，完成代码和报告后 push。Actions 自动测试，通过后上传累计成绩。

完整操作说明：[从 Fork 到自动评测](docs/FORK_GUIDE.md)。每个章节已经配好 CI，无需 GitHub Classroom，也无需向上游提交 PR。

## 分支与实验报告

| 分支 | 内容 | 分值 | 必须提交的报告 |
| --- | --- | ---: | --- |
| `main` | 课程入口与操作指南 | — | — |
| `ch1` | 应用程序与执行环境 | — | — |
| `ch2` | 批处理系统 | — | — |
| `ch3` | 多道程序与分时多任务 | 100 | `lab1` |
| `ch4` | 地址空间 | 100 | `lab1`、`lab2` |
| `ch5` | 进程管理 | 100 | `lab1` 至 `lab3` |
| `ch6` | 文件系统与 I/O | 100 | `lab1` 至 `lab4` |
| `ch7` | 进程间通信 | — | — |
| `ch8` | 并发与同步 | 100 | `lab1` 至 `lab5` |

报告放在 `reports/`，文件名为 `lab1.md` 或 `lab1.pdf` 等。请提交真实实验报告；后续章节仍需保留此前报告。

## 评分与同步

push 到 `ch3`、`ch4`、`ch5`、`ch6`、`ch8` 自动触发对应章节评测。官方测试全部通过、实验报告齐全且检查器成功退出，才记该章 100 分。重复通过不会重复加分，已通过章节的成绩会保留。

Actions 先执行 **Test chapter and reports**，通过后执行 **Save progress and upload score**。上传日志出现 `OpenCamp accepted the score (result=1).` 表示 OpenCamp 接口接受了成绩；再到学员成绩页面核对显示。

通过记录保存在个人仓库 `gh-pages` 分支的 `course-2073.json`。本仓库固定向课程 **2073** 上传，Secret 沿用 `ARCEOS_2026_SPRING_TOKEN` 这个名称。Token 只存入 Secrets，不写入仓库。

模板保留待完成的实验代码，直接运行时出现测试失败属于预期结果。`main`、`ch1`、`ch2`、`ch7` 不计分。

## 文档与来源

- [学员 Fork 与提交指南](docs/FORK_GUIDE.md)
- [课程配置和维护说明](docs/MAINTAINER.md)
- [验证记录与当前限制](docs/VALIDATION.md)
- [保留的 2026s 上游说明](docs/UPSTREAM-2026s.md)
- [rCore 实验指导](https://learningos.github.io/rCore-Tutorial-Guide/)
- [rCore 教程](https://rcore-os.github.io/rCore-Tutorial-Book-v3/)

本仓库由个人账号维护，保留上游源码历史，按 [GPL-3.0](LICENSE) 许可分发。
