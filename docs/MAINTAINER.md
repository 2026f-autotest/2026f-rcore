# 2026f rCore 组织维护流程

组织：`2026f-autotest`。模板：`2026f-autotest/2026f-rcore`。学员仓库：`2026f-autotest/2026f-rcore-登录名`。

## 版本与课程配置

| 项目 | 当前配置 |
| --- | --- |
| 课程源码 | [LearningOS 2026s rCore 模板](https://github.com/LearningOS/2026s-oscamp-professional-2026s-rcore-rCore-Tutorial-Code) |
| 来源 main 提交 | `6a82420303a607614293e5dd77951aafa564feec` |
| 检查器 | `LearningOS/rCore-Tutorial-Checker`，提交 `7d61ec55b58eed6ca7052917846c1b87af34563a` |
| 测试集 | `LearningOS/rCore-Tutorial-Test`，提交 `a0593662ad55d670ba8c27ce1763347cd0dd552f` |
| 运行镜像 | `alicesama/rcore-ci:2024a` |
| Rust | 各章原有 `nightly-2024-05-02` |
| OpenCamp 课程 | `2073` |
| 成绩上传 Secret | `ARCEOS_2026_SPRING_TOKEN` |
| 上传地址 | `https://api.opencamp.cn/web/api/courseRank/createByThirdToken` |
| 计分规则 | `ch3/ch4/ch5/ch6/ch8` 各 100 分，共 500 分 |

课程内容沿用 2026s 的各章节源码和历史，原始说明保存在 [UPSTREAM-2026s.md](UPSTREAM-2026s.md)，许可证为 GPL-3.0。

## 1. 配置模板和组织凭证

组织所有者把课程代码和 `main`、`ch1` 至 `ch8` 放入公开模板仓库，在仓库 Settings → General 勾选 **Template repository**。模板不要设置 `STUDENT_GITHUB`，避免将课程模板作为学员提交。

在[组织 Actions Secrets](https://github.com/organizations/2026f-autotest/settings/secrets/actions)添加 `ARCEOS_2026_SPRING_TOKEN`，值使用课程 2073 的上传 Token。当前组织已设置为 **Public repositories**，API 与首个学员仓库的 CI 已确认共享 Secret 可用，新建公开课程仓库无需逐仓库添加 Secret。建仓脚本也兼容日后改用指定仓库范围的情况。凭证名称沿用现有课程，实际上传课程固定为 2073。

GitHub Free 支持公开仓库使用组织 Secret。不要选择只允许私有仓库的策略。见[组织 Secret 文档](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets#creating-secrets-for-an-organization)。

## 2. 配置统一领取入口

自助入口为 [2026f-autotest/enroll](https://github.com/2026f-autotest/enroll)。维护者只需在该入口的仓库 Actions Secrets 配置一次 `ENROLL_GITHUB_TOKEN`，用于创建和配置本组织的课程仓库。该凭证不放入组织共享 Secret 或学员仓库。当前已配置，真实运行见[入口验证记录](https://github.com/2026f-autotest/enroll/blob/main/docs/VALIDATION.md)。

## 3. 学员自助申请

学员点击 README 中的领取链接，点击 **Create** 提交申请。Actions 从 `issue.user.login` 读取学员账号，复制 `main`、`ch1` 至 `ch8`，设置 `STUDENT_GITHUB`、分配该仓库写权限并触发配置检查。机器人回复仓库与邀请链接，学员接受邀请即可开始实验。助教无需名单收集或逐个建仓。

失败申请由维护者在领取入口的 Actions 输入原 Issue 编号重试；重试仍取原申请人的身份，不会绑定执行重试的助教。无需学员复制 Token 或安装 GitHub CLI。

## 4. 核对配置并让学员提交

建仓脚本配置完账号、凭证访问和权限后，会自动运行 **Check student configuration**。在 Actions 核对它通过；必要时也可手动运行。该工作流检查仓库名、`STUDENT_GITHUB` 和组织 Token 是否可用，不打印 Token、不调用 OpenCamp，也不表示课程 Token 已通过服务端验证。

学员完成[提交指南](STUDENT_GUIDE.md)。其 push 到评分章节会触发官方测试，通过后累计成绩并调用 OpenCamp。只有接口返回 `result=1` 才视为上传成功，最后核对 OpenCamp 学员成绩页面。

GitHub 从模板创建章节时会立即产生 push 事件；此时学员变量可能尚未写入。初始化期间的自动运行会跳过评测和配置检查，绑定完成后由脚本主动检查，后续学员 push 正常评测。

## 评测和身份规则

`build.yml` 负责触发和作业权限；`rcore_grade.py` 执行固定版本的官方检查器，保留真实退出状态、唯一测试摘要与报告检查；`rcore_publish.py` 保存已通过章节并上传。

每个作业仓库的变量 `STUDENT_GITHUB` 由建仓脚本写入 GitHub 官方返回的登录名。上传脚本要求组织为 `2026f-autotest`，仓库名为 `2026f-rcore-该登录名`，触发账号也匹配。维护者或机器人替别人 push 只会测试，不会上报为另一名学员。

累计记录保存在 `gh-pages:course-2073.json`。每章通过记 100 分，同章重试不重复加分。历史记录绑定课程、仓库与学员，不导入旧课堂的 `latest.json`。上传作业串行排队，先保存记录再调用接口；接口失败后可以重试。无需配置 GitHub Pages 网站。

## 更新课程公共文件

公共文件包括 `.github/` 下的工作流、脚本和回归测试，以及 README、docs、`enroll.py`、`students.example.txt` 和 `.gitignore`。应同步到 `main` 与 `ch1` 至 `ch8`，保留各章原始实验代码，不把整条章节分支互相合并。

模板更新不会自动进入已经分配的学员仓库。更新旧学员仓库时只同步明确修改的公共文件，并保留学员代码、报告和成绩历史。

## 本地应急建仓

保留 `enroll.py` 供维护者处理入口故障。已完成 GitHub CLI 登录的组织 Owner 在本课程目录执行 `python3 enroll.py 学员GitHub登录名`；也可按 `students.example.txt` 创建被忽略的 `students.txt` 后执行 `python3 enroll.py`。课程 Token 不传给脚本，日常接入使用自助领取入口。

## 领取完成的判断

自助入口先使用 `preparing-` 临时仓库名，准备期间评测和上传均跳过。入口等待本次配置检查实际通过后，分配权限，最后改成正式仓库名并回复邀请链接；失败保留临时仓库供重试。网络重试和排队规则见[入口维护流程](https://github.com/2026f-autotest/enroll/blob/main/docs/MAINTAINER.md)。已有正式学员仓库保留代码并重新检查。

## 自动化代码检查与上传重试

`check.yml` 自动执行本课程的自动化回归测试。备用 `enroll.py` 与领取入口使用同一份 `provision.py` 和 `github_api.py`；更新时同步这两份公共文件。

成绩 JSON 的 `upload.status` 为 `accepted` 时表示 OpenCamp 已返回 `result=1`；`pending` 表示尚未记录到接口确认，结合对应 Actions 日志处理。上传失败可重跑上传作业；已保存的真实测试结果不需要重新计算。

[本轮审查与验证记录](https://github.com/2026f-autotest/enroll/blob/main/docs/AUDIT.md)
