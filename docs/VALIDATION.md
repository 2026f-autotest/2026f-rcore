# 2026f rCore 验证记录

## 2026f-autotest 组织版（2026-09-14）

组织版已经实际创建首个学员仓库，完成身份绑定、共享 Secret 读取检查和 push 自动评测。当前完成 15 项回归检查，覆盖真实检查器输出解析、累计计分、上传业务错误、组织仓库与学员匹配、批量建仓的 API 顺序、重试保留代码与变量、错误权限停止。回归测试中的建仓用例使用模拟 API；以下另列真实 GitHub 操作结果。

```sh
python3 -m unittest discover -s .github/tests
```

`-s` 指定回归测试目录；测试不会创建远程仓库或上传真实成绩。Python 语法、两份工作流的 YAML 解析与 `git diff --check` 检查通过。

当前远程模板为 [2026f-autotest/2026f-rcore](https://github.com/2026f-autotest/2026f-rcore)，GitHub API 确认为公开模板（`is_template: true`）。`main`、`ch1` 至 `ch8` 的远端提交已逐个核对，公共配置相同，章节源码相对个人模板未改动。

真实 push 触发的 [ch3 运行 34773627267](https://github.com/2026f-autotest/2026f-rcore/actions/runs/34773627267) 已完成：容器初始化、检出源码、QEMU 测试和日志附件上传均正常。未完成的模板实际得到 `Test passed58547: 5/7`，检查器返回 2，评分结果为 `passed: false`，上传成绩作业跳过。测试失败属于未完成实验的预期结果。

```text
Panicked at src/bin/ch3_trace.rs:22, assertion failed: 3 <= count_syscall(SYSCALL_GETTIMEOFDAY)
Test passed58547: 5/7
AssertionError
make: *** [Makefile:118: test] Error 1
Process completed with exit code 2.
```

原始 GitHub 日志保存于维护者本地 `tmp/org-ch3-34773627267.log`；日志与结果 JSON 同时保存在该运行的附件中。模板仓库没有学员绑定，其配置检查按设计跳过。

### 真实建仓与共享凭证

维护者 `Alayfolk64` 已完成本机 GitHub CLI 登录。API 确认组织 Secret `ARCEOS_2026_SPRING_TOKEN` 存在，策略为 `all`，对应页面的 **Public repositories**。只读取 Secret 元数据，没有读取或输出凭证值。

实际执行 `python3 enroll.py Alayfolk64` 成功创建公开仓库 [2026f-rcore-Alayfolk64](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64)，包含 `main`、`ch1` 至 `ch8`；仓库变量 `STUDENT_GITHUB` 为 `Alayfolk64`。课程 Token 直接来自组织 Secret，学员仓库没有另行复制凭证。该账号已经是组织所有者，权限接口返回已可访问；普通外部学员接受邀请的步骤尚未用第二个账号实测。

重复执行建仓脚本也成功，前后九条分支的提交 SHA 完全一致，证明重试没有覆盖作业代码。脚本在配置完成后自动触发的 [配置检查 34774516977](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774516977) 已通过，实际日志为：

```text
Student mapping and organization secret are configured. No score was uploaded.
```

原始记录保存在维护者本地 `tmp/enroll-Alayfolk64.log`、`tmp/enroll-Alayfolk64-retry.log`、`tmp/student-heads-before-retry.json`、`tmp/student-heads-after-retry.json` 和 `tmp/student-config-34774516977.log`。

### 建仓时序问题与修复

第一次从模板生成仓库时，GitHub 立即触发各章 push 工作流，早于脚本写入 `STUDENT_GITHUB`。当时共享 Secret 已可用，但配置检查因学员变量为空失败；[原始失败 34774280008](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774280008) 保留如下错误：

```text
ValueError: STUDENT_GITHUB must be the student's GitHub login.
Process completed with exit code 1.
```

已修复为：学员变量未配置时，自动 push 运行跳过；建仓脚本完成身份、凭证访问与写入权限配置后，再主动触发配置检查。手动配置检查仍会报告缺失变量。修复已同步到模板与首个学员仓库的全部九条分支，修复后的自动配置检查和后续 push 配置检查均通过。

### 学员 push 实测

首个学员仓库的 `ch3` 提交 `aea5f32b4fa854ca59bb2bae5cd276413066d152` 实际触发两项工作流：

- [配置检查 34774565146](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774565146)：通过，确认身份映射与组织 Secret 可用。
- [章节评测 34774565145](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774565145)：运行真实 QEMU 与官方检查器，未完成实验得到 `5/7`，检查器退出状态为 2；日志附件上传成功，成绩上传作业跳过。

该次评测的真实失败片段：

```text
Panicked at src/bin/ch3_trace.rs:22, assertion failed: 3 <= count_syscall(SYSCALL_GETTIMEOFDAY)
Test passed27460: 5/7
AssertionError
make: *** [Makefile:118: test] Error 1
Process completed with exit code 2.
```

完整日志在维护者本地 `tmp/student-push-34774565145.log`。同一次运行的 `rcore-ch3-34774565145-1` 附件包含测试日志和结果 JSON。

首次建仓时自动触发的五章评测也已完成，结果与未完成的上游模板一致：

| 分支 | 官方测试通过数 | 检查器退出状态 | 学员仓库运行 |
| --- | --- | ---: | --- |
| `ch3` | 5/7 | 2 | [34774280011](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774280011) |
| `ch4` | 4/16 | 2 | [34774281032](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774281032) |
| `ch5` | 2/15 | 2 | [34774282597](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774282597) |
| `ch6` | 2/31 | 2 | [34774283404](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774283404) |
| `ch8` | 22/25 | 2 | [34774285497](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34774285497) |

本轮证明建仓、共享凭证、身份配置、自动触发和未通过时阻止上传均可用。配置检查只验证 Token 存在，不验证 OpenCamp 服务端是否接受它；本轮未完成真实 rCore 成绩上传验收，也未向真实课程上传模拟分数。正向上传需由学员完成实验和报告后，核对上传作业 `result=1` 及 OpenCamp 学员成绩页面。

## 个人仓库版本的历史证据

以下为 Alayfolk64/2026f-rcore 的既有验证，仅证明对应版本与日期的结果。组织版评分检查器未修改，学员识别及建仓流程需要上述独立验证。旧版 setup.py 的个人 Fork 初始化已经从组织版移除。


本记录区分测试逻辑、真实检查器执行、GitHub 运行和 OpenCamp 接口，不把模拟验证写成真实成绩上传。

### 已完成的基础检查

- Python 语法和工作流 YAML 语法检查通过。
- 章节成绩可按任意顺序累计，同一章节重试不重复计分，五章最高 500 分；不完整的通过结果以及其他用户的历史记录被拒绝。
- 在本地独立 Git 仓库中实际执行了 `gh-pages` 创建、章节记录提交和推送；覆盖上传拒绝后重试与五章累计。只有 HTTP 调用使用模拟响应，未向 OpenCamp 写入测试分数。
- 上传接口的非 JSON 响应和 `result` 不为 1 的响应均视为失败。

回归测试入口：

```sh
python3 .github/tests/test_grading.py
```

在仓库根目录执行，检查官方随机后缀输出解析、非法结果拒绝、章节累计及接口业务错误处理；不会访问网络或上传成绩。

### 真实检查器验证

使用原有已完成的 ch3 作业在独立本地 checkout 验证，代码没有加入课程模板。镜像为 `alicesama/rcore-ci:2024a`，拉取摘要为 `sha256:6e5706f0cfb8e5d3cf705d6c1069b42865e6ca11c5945a38588d58c2bad903e4`。

首次执行 QEMU 测试得到 `Test passed10564: 7/7`，报告检查成功，官方检查器退出状态 0。包装脚本最初只识别无后缀的 `Test passed:`，导致误判失败；已修正为兼容官方随机数字后缀，并添加真实输出回归用例。

修正后从全新 checkout 再次完整执行，实际结果为 `Test passed54729: 7/7`、`Report for lab1 found.`，包装脚本退出状态 **0**，结果为 `passed: true`、`points: 7/7`。因此编译、QEMU、官方检查器、报告检查和结果解析的正向链路已经实际通过。

### 仓库与 GitHub 验证

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

### OpenCamp 同步验证范围

此前课程 2073 的基础练习联调使用同一个 Token，实际调用接口得到 `OpenCamp accepted the score (result=1).`，证明当时该账号加入训练营后接口接受了请求。该次为 **0/100 的基础练习**，不是本套 rCore 的五章 500 分验收。

本模板按 rCore 原规则配置 500 分累计。未将模拟的 500 分上传到真实课程，也未宣称已经核对 OpenCamp 网页上的 500 分显示。

### 个人版初始化脚本验证（2026-09-14，组织版建仓之前）

新增 `setup.py`，把手动设置 Secret 和启用 Actions 合并为一次运行。全部 13 项回归测试通过，其中 8 项覆盖初始化流程。对命令执行边界进行模拟验证，覆盖首次登录、取消登录、首次设置、重复运行保留凭证、错误账号拒绝、缺少章节拒绝、写入失败停止，以及远端地址校验。课程 Token 通过标准输入传给 GitHub CLI，不进入命令参数或源码文件。

```sh
python3 -m unittest discover -s .github/tests
```

在仓库根目录执行全部回归测试；`-s` 指定测试文件所在目录。当时 GitHub CLI 的真实 Secret 写入及第二个学员账号的完整初始化尚未运行，CLI 登录检查返回 `You are not logged into any GitHub hosts. To log in, run: gh auth login`。这是个人版阶段的历史状态；组织版已完成登录和首个真实建仓，见本页开头。这些模拟用例不代表第二个真实账号已经配置成功。

本次未修改评分工作流、检查器或上传协议，之前五个分支的真实 CI 验证仍对应当前评分实现。

## 自助领取与秋冬季页面核对（2026-09-14）

统一入口 [2026f-autotest/enroll](https://github.com/2026f-autotest/enroll) 已启用。真实 [申请 #1](https://github.com/2026f-autotest/enroll/issues/1) 在配置建仓凭证后重试成功，读取原申请人 `Alayfolk64`，配置已有学员仓库并回复链接；[配置检查 34777555641](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34777555641) 成功。普通外部学员接受邀请尚未用第二个账号实测。

已只读核对 [OpenCamp 秋冬季 rCore 阶段](https://opencamp.cn/os2edu/camp/2026fall/stage/5) 的公开页面数据，课程编号为 2073。页面使用的排行榜查询接口返回 `Alayfolk64` 的已有 0 分记录；该记录并非本轮 rCore 章节上传，不改变上文正向上传尚待完成实验的验收范围。未修改 OpenCamp 后台。
