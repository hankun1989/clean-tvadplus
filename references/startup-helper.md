# 老固件开机恢复与启动助手

本助手是该 MiTV4A 最终成功配置的一部分，与 CMFA、完整规则和首次系统 VPN 授权共同部署。同类已确认设备直接使用这套组合；其他固件先核对 [兼容性门槛](compatibility.md)与用户已有后台管理设置，特别是 Android 15 安装限制和其他品牌桌面触发。

## 实机结果

用户批准启用后，Android 系统在开机时绑定该服务，助手通过 CMFA 官方 START_CLASH 入口启动过滤。完整重启后约 39 秒观察到两项服务自动运行，用户未手动启动工具，从“我的应用 → 芒果 TV”播放并确认直接进入正片。

最终14条配置再次整机重启，约30秒观察到助手与过滤服务自动运行，用户随后确认所测几个入口均无广告。其他固件、不同版本和更早的开机时点应重新验证。

## 助手内容与权限

- 包名：`io.github.hankun1989.tvfilterstarter`；版本 `0.1.0`，minSdk/targetSdk 23。
- [实测 APK](../assets/电视过滤启动助手_0.1.0.apk)，SHA-256：`b2ff74d472e0f7c53f08f870c3fa161fa9303fc7016c493ece06191d264dad9a`。
- [完整源码](../assets/starter-source/)与 [构建脚本](../scripts/build_starter.py)。APK 的非签名成员已与公开源码重建结果逐项一致验证。
- 唯一 uses-permission 为 `ACCESS_NETWORK_STATE`，没有 INTERNET 权限。服务受系统 `BIND_ACCESSIBILITY_SERVICE` 保护。
- 只接收小米桌面的窗口状态事件元数据；不读取屏幕节点/文字、通知内容或按键。`canRetrieveWindowContent` 和 `canRequestFilterKeyEvents` 均为 false。
- 服务连接后在 1.5、10、30、60、120 秒检查，返回桌面也会触发检查；已有任何 VPN 连接时保持该连接，不冒充已验证的过滤状态。
- 助手只发启动请求，不能代替首次 VPN 授权、配置选择、规则验证，也不是持续轮询的后台守护。

## 启用

先确保 CMFA 已完成首次系统 VPN 确认、正确配置已激活、实际过滤已验证。向用户说明辅助功能服务的上述范围，获得安装和启用授权后再继续。使用 `SERIAL` 明确选择用户授权的单台电视。

```sh
adb -s "$SERIAL" install /absolute/skill/assets/电视过滤启动助手_0.1.0.apk
python3 scripts/configure_starter.py --serial "$SERIAL" \
  --enable --state-file /absolute/task/work/starter-state.json
```

脚本保存权限为 0600 的原始状态，追加本助手而保留原有辅助功能服务。原来总开关关闭时才打开；重复运行保留第一次快照。若该固件拒绝设置写入，停止并核对用户可达的系统设置，不能宣布启用成功。

确认系统实际绑定服务及启动日志，而不只是 secure 设置字符串存在：

```sh
adb -s "$SERIAL" shell dumpsys activity services io.github.hankun1989.tvfilterstarter
adb -s "$SERIAL" shell dumpsys activity services com.github.metacubex.clash.meta
adb -s "$SERIAL" logcat -d -v threadtime 'TVFilterStarter:I' '*:S'
```

随后在用户授权范围内整机重启。用户先不手动打开任何助手/过滤工具，直接测试原来有长广告的视频；结合开机时间、服务与流量日志判断。调试连接中断时先保留现场，不用手动启动来伪装自动恢复。

## 暂停与恢复

打开“电视过滤启动助手”可暂停自动启动。要关闭过滤，还需在 CMFA 内停止，避免助手随后再次启动。

需要撤销本次启用时：

```sh
python3 scripts/configure_starter.py --serial "$SERIAL" \
  --restore --state-file /absolute/task/work/starter-state.json
```

脚本只移除本次新增的助手条目，保留之后新增的其他服务；原总开关关闭且当前列表仍等于原列表时才恢复关闭。若助手本来已经存在，恢复不会删除它。卸载助手按用户意愿进行，不把重置其他服务当成还原。

## 自行构建

需要本地 JDK 17 与含 aapt、zipalign、D8、apksigner 的 Android Build Tools，以及 Android 平台 android.jar；构建不会自动下载工具。示例参数使用自行安装的实际路径：

```sh
python3 scripts/build_starter.py --java-home /absolute/local/jdk \
  --build-tools /absolute/local/android/build-tools \
  --android-jar /absolute/local/android/platform/android.jar \
  --build-dir /absolute/task/work/starter-build
```

构建目录含私有签名材料，妥善保留以更新自己编译的安装包，绝不提交仓库。自行生成的新签名不能直接覆盖仓库原签名的已安装助手；更换前先保留原状态并取得相应授权。无需为普通复用重新构建实测 APK。
