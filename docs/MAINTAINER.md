# 2026f rCore 维护说明

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

这是个人账号维护的 2026f 课程模板，保留 2026s 各章源码与历史；不代表上游另行发布了 2026f 版本。原始 main 说明保存在 [UPSTREAM-2026s.md](UPSTREAM-2026s.md)。GPL-3.0 许可证与原源码一并保留。

## 执行链路

`.github/workflows/build.yml` 负责触发和权限；`.github/scripts/rcore_grade.py` 负责执行固定版本的官方测试；`.github/scripts/rcore_publish.py` 负责累计通过章节及上传成绩。

测试作业不注入成绩上传 Token。它保留 `make test` 的真实退出状态，同时要求唯一的 `Test passed: N/M` 结果为满分，因此报告缺失导致的失败不会被输出解析覆盖。通过结果才传给上传作业。

上传作业只接受个人仓库所有者触发的运行，使用 `contents: write` 保存成绩记录。API 请求中的 `name` 取 `github.repository_owner`，`courseId` 固定 2073，`totalScore` 固定 500。接口 HTTP 成功但业务字段 `result` 不为 1 时，任务仍失败。

## 章节累计与重试

累计记录为 `gh-pages:course-2073.json`，包含课程、仓库、用户、通过章节及对应代码提交。脚本会拒绝不同课程或账号的历史；不会导入旧课堂的 `latest.json`。不需要配置 GitHub Pages。

先保存章节记录，再调用上传接口。上传失败后重试仍使用已保存记录；同一章节最多贡献 100 分。上传作业按仓库串行排队，采用 `queue: max`，最多保留 100 个等待作业，避免连续提交时覆盖尚未记录的章节。参考 [GitHub 并发队列说明](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)。

## 更新模板

`main` 与 `ch1` 至 `ch8` 都预装相同的三个 CI 文件。修改公共流程后，把明确修改的 CI 文件同步到各章并分别提交；不要合并不同章的完整代码树。README 和课程文档也应保持一致。

学员 Fork 并克隆后运行 `python3 setup.py`，首次按提示登录 GitHub、输入课程 Token，脚本自动保存 Secret 并启用 Actions。`setup.py` 和 `.github/tests/test_setup.py` 也应同步到所有章节。它只配置当前个人仓库，校验登录账号、仓库所有者及章节是否齐全；已有 Secret 保留原值。发布前检查全部九个分支存在、章节源码与选定上游基线一致、真实检查器可以运行、上传脚本正确处理拒绝与重试。验收范围见 [VALIDATION.md](VALIDATION.md)。

Token 通过课程已有受控渠道提供，公开仓库只出现 Secret 名称。课程 2073 和凭证已沿用此前确认的配置；本模板不涉及修改 OpenCamp 后台。

个人 Fork 的所有者能够修改自己的 CI 与成绩记录，因此这套流程提供课程练习的自动评测和同步；如将其用于需要防篡改的正式考试，评分应另由管理员控制的执行环境完成。
