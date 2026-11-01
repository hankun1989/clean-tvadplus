# 老款小米电视去广告 Skill

适用于 Codex、Qoder 等支持 `SKILL.md` 的 Agent。基于 **2018 年 MiTV4A / Android 6.0.1** 实机排查：保留原小米桌面，在电视本机过滤广告连接，处理视频 SDK 自带解析绕过普通 DNS，以及老固件重启后过滤不恢复的问题。

## 实测范围

| 入口 | 本次实际结果 |
|---|---|
| 小米桌面视频《大梦归离》 | 原约 110–127 秒片头 → 直接进入正片 |
| 我的应用 → 芒果 TV | 直接进入正片；完整重启后仍直接进入正片 |
| 我的应用 → 云视听极光《小马宝莉》 | 一百多秒片头消失；旧 15 秒化妆品开屏在用户同意单独重置该应用后消失 |
| 我的应用 → 银河奇异果 | 用户确认直接进入正片；该次片名未提供 |

启动助手已通过完整重启及芒果播放验证；最终 14 条配置再次重启后，约 30 秒时只读观察到助手与过滤服务自动启动，用户随后确认上述几个入口均无广告，全程未手动打开过滤工具或助手。详见[证据与范围](references/evidence.md)。不保证所有平台、所有广告或未来版本永久有效。

过滤不解锁付费片源、会员清晰度等权益。普通内容本地直连，无需代理订阅；不要求换桌面、root、刷机或卸载系统包。

## 新款与其他品牌

已补充 [兼容性评估与 Android 14 模拟测试](references/compatibility.md)：通用系统上的安装、实际连接过滤及正常系统重启恢复通过；其他品牌电视的真实视频播放尚未验证。

当前启动助手 0.1.0 不能在 Android 15 上按普通流程首次安装，其他品牌桌面触发也需要适配。按系统版本和 CPU 选择路径，不将本例整套原样套用到所有电视。

## 安装 Skill

Codex：

```sh
git clone https://github.com/hankun1989/legacy-xiaomi-tv-adblock.git \
  ~/.codex/skills/legacy-xiaomi-tv-adblock
```

Qoder 可放入其用户 Skill 目录，如 `~/.qoder/skills/legacy-xiaomi-tv-adblock`。目录已存在时先核对，不覆盖用户修改，再刷新 Agent 的 Skill 列表。

示例请求：

> 使用 $legacy-xiaomi-tv-adblock 排查我的老款小米电视广告，保留原桌面，分别验证桌面和独立应用，并测试完整重启后自动恢复。

安装 Skill 只增加指引、脚本和可审阅资源，不会自动连接或修改电视。

## 资源与使用

- [SKILL.md](SKILL.md)：Agent 判断与流程入口。
- [安装与工作流](references/workflow.md)：官方 CMFA 兼容包、配置、首次系统授权、验证和还原。
- [启动助手](references/startup-helper.md)：老固件开机限制、最小助手权限、启用与撤销、实测 APK 和完整源码。
- [云视听旧开屏缓存](references/tencent-startup-cache.md)：为什么只拦域名或普通清缓存仍可能显示旧广告；单应用重置必须单独授权。
- [案例证据](references/evidence.md)：实际测试与判断边界。
- `scripts/make_profile.py`：生成含独立口令的私有运行配置，规则起点见 `assets/ad-domains.txt`。
- `scripts/transfer_profile.py`：仅经 ADB reverse 与电脑回环地址传送，也支持刷新既有配置。
- `scripts/configure_starter.py`：启用或撤销本助手，保存原始状态并保留其他辅助功能服务。
- `scripts/build_starter.py`：使用本地 Android SDK/JDK 重建助手；普通使用不必重新构建。

Python 脚本仅用标准库；设备操作需要 `adb`。第三方过滤应用从[官方 CMFA 项目](https://github.com/MetaCubeX/ClashMetaForAndroid)取得并核验，本仓库只附自有启动助手 APK 及源码，不附第三方 APK。

## 数据与还原

助手没有联网权限，不读取屏幕文字、通知或按键；启用辅助功能前解释范围并取得授权。默认保留账号；确需重置目标应用时，先说明退出登录和本地记录等损失，再取得明确同意。

仓库不含家庭 IP、账号、设备标识、原始日志/截图、运行配置或私有签名材料。出现播放异常，暂停启动助手并停止过滤或回退新增规则，参见[还原流程](references/workflow.md#6-还原与收尾)。

原创文档、脚本和启动助手源码使用 [MIT License](LICENSE)。第三方应用遵循各自许可。
