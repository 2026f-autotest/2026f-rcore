# 2026f rCore 验证记录

## 2026f-autotest 组织版（2026-09-14）

组织版在个人仓库版本基础上调整身份绑定与学员接入。当前完成 15 项回归检查，覆盖真实检查器输出解析、累计计分、上传业务错误、组织仓库与学员匹配、批量建仓的 API 顺序、重试保留代码与变量、错误权限停止。建仓测试使用模拟 API 响应，不能代替 GitHub 上实际建仓验证。

```sh
python3 -m unittest discover -s .github/tests
```

`-s` 指定回归测试目录；测试不会创建远程仓库或上传真实成绩。Python 语法与 `git diff --check` 检查通过。

当前远程模板为 `2026f-autotest/2026f-rcore`。组织 Secret 与真实学员仓库的验证结果将在实际运行后记录。

## 个人仓库版本的历史证据

以下为 Alayfolk64/2026f-rcore 的既有验证，仅证明对应版本与日期的结果。组织版评分检查器未修改，学员识别及建仓流程需要上述独立验证。旧版 setup.py 的个人 Fork 初始化已经从组织版移除。


本记录区分测试逻辑、真实检查器执行、GitHub 运行和 OpenCamp 接口，不把模拟验证写成真实成绩上传。

## 已完成的基础检查

- Python 语法和工作流 YAML 语法检查通过。
- 章节成绩可按任意顺序累计，同一章节重试不重复计分，五章最高 500 分；不完整的通过结果以及其他用户的历史记录被拒绝。
- 在本地独立 Git 仓库中实际执行了 `gh-pages` 创建、章节记录提交和推送；覆盖上传拒绝后重试与五章累计。只有 HTTP 调用使用模拟响应，未向 OpenCamp 写入测试分数。
- 上传接口的非 JSON 响应和 `result` 不为 1 的响应均视为失败。

回归测试入口：

```sh
python3 .github/tests/test_grading.py
```

在仓库根目录执行，检查官方随机后缀输出解析、非法结果拒绝、章节累计及接口业务错误处理；不会访问网络或上传成绩。

## 真实检查器验证

使用原有已完成的 ch3 作业在独立本地 checkout 验证，代码没有加入课程模板。镜像为 `alicesama/rcore-ci:2024a`，拉取摘要为 `sha256:6e5706f0cfb8e5d3cf705d6c1069b42865e6ca11c5945a38588d58c2bad903e4`。

首次执行 QEMU 测试得到 `Test passed10564: 7/7`，报告检查成功，官方检查器退出状态 0。包装脚本最初只识别无后缀的 `Test passed:`，导致误判失败；已修正为兼容官方随机数字后缀，并添加真实输出回归用例。

修正后从全新 checkout 再次完整执行，实际结果为 `Test passed54729: 7/7`、`Report for lab1 found.`，包装脚本退出状态 **0**，结果为 `passed: true`、`points: 7/7`。因此编译、QEMU、官方检查器、报告检查和结果解析的正向链路已经实际通过。

## 仓库与 GitHub 验证

`main` 和 `ch1` 至 `ch8` 已推送至 [Alayfolk64/2026f-rcore](https://github.com/Alayfolk64/2026f-rcore)。逐分支与 2026s 上游提交比较，差异仅为 CI、课程文档和忽略规则，章节实验源码没有修改。各分支的评分工作流和脚本保持一致。

已在仓库设置中添加 `ARCEOS_2026_SPRING_TOKEN`，GitHub 显示 `Repository secret added.`；公开文件不包含凭证值。

2026-09-11 实际向五个评分分支 push，全部自动触发。以下结果来自未完成实验的上游模板，**测试失败是预期结果**：

| 分支 | 官方测试通过数 | 检查器退出状态 | GitHub 运行 |
| --- | --- | ---: | --- |
| `ch3` | 5/7 | 2 | [运行记录](https://github.com/Alayfolk64/2026f-rcore/actions/runs/34525042217) |
| `ch4` | 4/16 | 2 | [运行记录](https://github.com/Alayfolk64/2026f-rcore/actions/runs/34525126176) |
| `ch5` | 2/15 | 2 | [运行记录](https://github.com/Alayfolk64/2026f-rcore/actions/runs/34525135684) |
| `ch6` | 2/31 | 2 | [运行记录](https://github.com/Alayfolk64/2026f-rcore/actions/runs/34525146286) |
| `ch8` | 22/25 | 2 | [运行记录](https://github.com/Alayfolk64/2026f-rcore/actions/runs/34525167984) |

五次运行均成功拉取镜像、检出源码、执行官方检查器并保存日志及 JSON 附件；失败结果被正确解析，成绩上传作业全部跳过。`ch3` 原始失败包括：

```text
Panicked at src/bin/ch3_trace.rs:22, assertion failed: 3 <= count_syscall(SYSCALL_GETTIMEOFDAY)
Test passed14832: 5/7
AssertionError
make: *** [Makefile:118: test] Error 1
Process completed with exit code 2.
```

这证明未完成的模板不会被误判为通过。对应的完整通过场景已在上面的本地独立 checkout 实测为 7/7；未把已完成作业发布到模板，也未让模板仓库上传练习成绩。

## OpenCamp 同步验证范围

此前课程 2073 的基础练习联调使用同一个 Token，实际调用接口得到 `OpenCamp accepted the score (result=1).`，证明当时该账号加入训练营后接口接受了请求。该次为 **0/100 的基础练习**，不是本套 rCore 的五章 500 分验收。

本模板按 rCore 原规则配置 500 分累计。未将模拟的 500 分上传到真实课程，也未宣称已经核对 OpenCamp 网页上的 500 分显示。

## 初始化脚本验证（2026-09-14）

新增 `setup.py`，把手动设置 Secret 和启用 Actions 合并为一次运行。全部 13 项回归测试通过，其中 8 项覆盖初始化流程。对命令执行边界进行模拟验证，覆盖首次登录、取消登录、首次设置、重复运行保留凭证、错误账号拒绝、缺少章节拒绝、写入失败停止，以及远端地址校验。课程 Token 通过标准输入传给 GitHub CLI，不进入命令参数或源码文件。

```sh
python3 -m unittest discover -s .github/tests
```

在仓库根目录执行全部回归测试；`-s` 指定测试文件所在目录。GitHub CLI 的真实 Secret 写入及第二个学员账号的完整初始化尚未运行，本机 CLI 登录检查返回 `You are not logged into any GitHub hosts. To log in, run: gh auth login`。这些模拟用例不代表第二个真实账号已经配置成功。

本次未修改评分工作流、检查器或上传协议，之前五个分支的真实 CI 验证仍对应当前评分实现。
