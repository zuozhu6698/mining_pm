# 第 2 批文件操作手册

> 跟着这个文档做，**20 分钟内**你就能让 Codex 开始干活。

---

## 总览

```
✅ 已完成：bootstrap-180.sh + GitHub 仓库 + 飞书 + Codex 授权
⏳ 现在做：把第 2 批文件 push 到 GitHub + 让 180 拉这个 app + 派 T001
```

## 一、解压第 2 批到本地仓库

把 tar 包解压到 `D:\Project\mining_pm`，**覆盖**已有文件（仓库目前是空的）。

PowerShell：

```powershell
cd D:\Project
# 假设 tar 包已经下载到 D:\Project\mining_pm_codex_batch2.tar.gz
tar -xzf mining_pm_codex_batch2.tar.gz -C D:\Project\
# 解压后会得到 D:\Project\mining_pm_batch2\，把里面的内容移到 mining_pm
# 用 robocopy 合并
robocopy D:\Project\mining_pm_batch2 D:\Project\mining_pm /E /MOVE
```

或者**用资源管理器**：
- 双击 tar 包解压
- 把里面所有内容（不含外层 mining_pm_batch2 目录）拖到 `D:\Project\mining_pm`

## 二、检查文件结构

```powershell
cd D:\Project\mining_pm
dir
```

预期看到：
```
AGENTS.md
.github\
apps\
docs\
scripts\
```

## 三、首次 push 到 GitHub

```powershell
cd D:\Project\mining_pm
git add .
git status   # 应该看到所有新文件
git commit -m "feat: initial scaffold with AGENTS.md, CI/CD, app skeleton"
git push -u origin main
```

push 完成后，**飞书会收到一条通知**（如果你的 deploy.yml 触发了——其实第一次 push 不会触发部署，因为 180 上还没装 app）。

## 四、让 180 上初次安装 mining_pm app

⚠️ **这一步是一次性的**——bench 第一次"认识"你的 app。之后所有更新都通过 git pull 完成。

PuTTY 进 180，跑：

```bash
sudo su - frappe
cd ~/frappe-bench

# 从 GitHub clone app
# 用 mining_deploy 账号配的 SSH key
bench get-app https://github.com/zuozhu6698/mining_pm --branch main

# 装到 site
bench --site mining.local install-app mining_pm

# 重启服务
exit
sudo supervisorctl restart all
```

⚠️ 如果 `bench get-app` 卡在 HTTPS 认证，改用 SSH：

```bash
# 配置 frappe 用户的 GitHub SSH（先在 8.13 复制密钥到 180）
# 或者用 HTTPS + token
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

简单版：用 HTTPS clone（公开仓库直接行；私有仓库需要 token）。

最稳妥：**让 GitHub Actions deploy.yml 第一次部署时自动 clone**——但这要求 deploy.yml 里加 fallback 逻辑。

→ **本期建议**：先手动跑 `bench get-app`，把 app clone 到 180。

跑完后检查：

```bash
sudo -u frappe bench --site mining.local list-apps
```

应该看到 `frappe` 和 `mining_pm`。

## 五、配置 GitHub Actions Secrets 的 SSH key

bootstrap 跑完后的 mining_deploy 用户已经在 180 上，但你还没把 8.13 的 mining_deploy 私钥贴到 GitHub Secrets。

```powershell
# 8.13 PowerShell
Get-Content $HOME\.ssh\mining_deploy
```

**这会输出私钥**——⚠️ **整段（含 BEGIN/END）** 复制到剪贴板。

浏览器打开：
```
https://github.com/zuozhu6698/mining_pm/settings/secrets/actions
```

找到 `DEPLOY_SSH_KEY`（之前是 `TODO`）→ **Update** → 把私钥粘贴进去 → Save。

⚠️ 然后**销毁这段剪贴板内容**（复制别的东西覆盖一下）。

## 六、把 mining_deploy 公钥贴到 180

8.13 上：

```powershell
Get-Content $HOME\.ssh\mining_deploy.pub
```

复制一行（`ssh-ed25519 AAAA... github-actions-deploy`）。

进 180：

```bash
ssh sdjg@192.168.8.180
sudo su - mining_deploy
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys <<'EOF'
ssh-ed25519 AAAA<刚才复制的内容> github-actions-deploy
EOF
chmod 600 ~/.ssh/authorized_keys
exit
exit
```

## 七、Branch Protection（终于可以配了）

仓库已经有 main 分支了。回到：

```
https://github.com/zuozhu6698/mining_pm/settings/branches
```

- Add branch protection rule
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- Save

## 八、在 GitHub 创建 T001 issue

浏览器打开：

```
https://github.com/zuozhu6698/mining_pm/issues/new?template=codex-task.md
```

- **标题**：`T001: Engineering Project DocType`
- **body**：把 `docs/T001-engineering-project-issue.md` 的全部内容复制粘贴进去
- **labels**：选 `codex-task`、`priority-p0`、`doctype`
- 提交创建

记下 issue 编号（比如 `#1`）。

## 九、派任务给 Codex

打开桌面端 Codex，选 `mining_pm` 项目。

在对话框里输入：

```
请实现 GitHub issue #1（T001 Engineering Project DocType）。

具体要求请读：
1. 仓库根目录的 AGENTS.md（项目宪法）
2. docs/frappe-patterns/01-doctype-basics.md（Frappe 模式库）
3. 在 GitHub 上看 issue #1 的完整 Field Specification

完成后请：
1. 创建分支 feat/T001-engineering-project
2. 写完 3 件套（json/py/test_py）
3. 跑 python scripts/validate-doctype.py 自验证
4. commit + push
5. 开 PR，标题用 issue 标题，描述里写 "Closes #1"
```

点提交，让 Codex 干活。

## 十、等 Codex 完成

Codex 桌面端会：
1. 读 AGENTS.md
2. 读模式库
3. 创建分支
4. 写文件
5. 跑 validate-doctype
6. push + 开 PR

预计 10-30 分钟。期间你可以做别的事。

## 十一、Review PR + Merge

PR 开了后：
1. 飞书会收到 PR 通知
2. 你打开 PR，看 diff
3. 满意了点 Merge

Merge 后 deploy.yml 自动触发：
- SSH 到 180
- git pull
- bench migrate
- bench build
- supervisor restart
- 健康检查
- 飞书推送"部署成功"

## 十二、浏览器验证效果

```
http://192.168.8.180/app/engineering-project
```

看到 Engineering Project 列表页（空的）+ "新增"按钮 = 成功 🎉

新增一条试试，能正常存储 = 端到端流程跑通。

---

## 卡点求救

| 现象 | 怎么办 |
|---|---|
| Codex 写错了 | 在 PR 评论里指出问题 + close PR + 重新派任务 |
| CI 失败 | 看 GitHub Actions 日志 |
| 部署失败 | 看飞书通知 + GitHub Actions deploy.yml 日志 |
| 浏览器 404 | bench migrate 没跑成功，去 180 查日志 |
| 不知道改啥 | 截图发我 |

---

完成 T001 后**回到这里**，我们继续 T002-T005。
