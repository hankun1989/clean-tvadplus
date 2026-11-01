# 最终安装、验证与还原流程

## 1. 确认设备

`SERIAL` 是经 `adb devices -l` 确认、用户授权的单台电视，不预填家庭地址。

```sh
adb devices -l
adb -s "$SERIAL" shell getprop ro.product.model
adb -s "$SERIAL" shell getprop ro.build.version.release
adb -s "$SERIAL" shell getprop ro.product.cpu.abilist
```

保留原桌面与账号；记录实际入口及原有网络/VPN。该过滤使用系统 VPN 通道，已有其他 VPN 时先协调其用途。桌面视频与独立应用分别验收。

## 2. 安装已验证的官方工具

本例采用 **CMFA 2.11.36.Meta / armeabi-v7a**，与 Android 6.0.1 实机兼容：

- [官方项目](https://github.com/MetaCubeX/ClashMetaForAndroid)
- [实测发行 v2.11.36](https://github.com/MetaCubeX/ClashMetaForAndroid/releases/tag/v2.11.36)
- 资产名：`cmfa-2.11.36-meta-armeabi-v7a-release.apk`
- SHA-256：`bd500e3d04e619e8d85e8ca196c8fd42de285fc5d3811e4cd3ee5dc355cd7dea`

从官方发行页获取匹配 CPU 的包并核验。其他固件/版本重新核对兼容性，不把这个版本永久当成最新。第三方 APK 放任务 work，不提交仓库。

```sh
adb -s "$SERIAL" install /absolute/task/work/cmfa.apk
```

## 3. 一次生成完整最终配置

在 Skill 目录运行：

```sh
python3 scripts/make_profile.py --output /absolute/task/work/tv-filter.yaml
python3 scripts/transfer_profile.py --serial "$SERIAL" \
  --profile /absolute/task/work/tv-filter.yaml --seconds 180
```

生成器采用全部 14 条实测规则、Sniffer 与 DIRECT 出站，含独立随机口令并以 0600 创建，拒绝覆盖已有文件。HTTP/TLS 域名识别覆盖本例 SDK 自带解析连接；正常内容本地直连。

传送只监听电脑回环地址、仅提供一个端点，经所选设备 ADB reverse 传送；退出会撤销自己的映射。端口已占用时换 `--device-port`，不覆盖其他映射，不向局域网开放带口令的目录服务器。

电视点保存，“Age 私钥”留空，自动更新禁用。选中 `TV-ad-filter` 为活动配置，返回主界面点启动并完成系统 VPN 确认。显式 `type: direct` 出站满足本例版本导入器要求，无需节点订阅。

更新同一配置时用相同设备端口加 `--refresh-only`，再从该配置菜单点“更新”，避免重复同名副本。

配置依据：[Sniffer](https://wiki.metacubex.one/en/config/sniff/)、[DIRECT](https://wiki.metacubex.one/en/config/proxies/direct/)。

## 4. 配置开机恢复

在 CMFA“设置 → 应用”打开“自动重启”，再按 [启动助手](startup-helper.md) 启用本仓库已实测的最小助手。先说明权限并取得授权，保留其他辅助功能服务及原始状态文件。

同类已确认机型直接完成这套组合；不要只装一部分就反复重启测试。助手通过官方 START_CLASH 入口启动已授权、已选好配置的工具；首次系统 VPN 确认仍由 CMFA 主界面完成。

## 5. 实际验收

逐项确认：正确配置激活、系统 VPN/TUN 建立、`Sniffer is loaded and working`、实际广告连接 REJECT、正片连接 DIRECT，以及用户看到正常正片。

样本覆盖用户所需的桌面与独立应用入口，分别观察开屏和片头。独立云视听的旧开屏处理见 [专门流程](tencent-startup-cache.md)。保留共享内容域，不根据泛化域名清单扩大封禁。

最终配置完整重启后，用户先不手动打开助手或过滤工具，直接播放原来有广告的内容；结合开机时间、服务与画面验收。启动有初始化间隔，不由单次结果推断任意早的时点都已开始过滤。

调试断开时核对当前 IP、网络连通性、5555 端口和握手。保留用户播放现场，不为诊断手动启动过滤来掩盖自动恢复状态，不终止其他任务共用的 ADB 服务。

## 6. 还原与收尾

1. 先在启动助手内暂停，或按原始状态文件撤销本次助手条目，再在 CMFA 内停止过滤。首次系统授权完成后也可用该版本官方 STOP_CLASH 入口。
2. 不再使用时按用户意愿卸载助手/过滤工具。仅撤销本次范围；其他历史系统包或路由器设置按其原始备份单独恢复。
3. 确认正常网络和正片播放；关闭本任务临时服务器、采集及自己的 reverse/forward，保留配置与恢复材料。用完可关闭电视调试。
4. 按任务文件规则清理本次已确认可再生成的副本，保留必要资源及原始材料。

本方案的正常内容本地直连，无需电脑代理节点。用户原有“路由器 DNS 指向电脑”属于另一项设置，不能声称已被自动撤销。
