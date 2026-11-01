package io.github.hankun1989.tvfilterstarter;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ComponentName;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public final class MainActivity extends Activity {
    private TextView status;
    private Button pause;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(60, 40, 60, 40);
        TextView title = new TextView(this);
        title.setText("电视过滤启动助手 0.1.0"); title.setTextSize(25); root.addView(title);
        TextView description = new TextView(this);
        description.setText("只负责自动启动已安装的过滤工具。\n不联网、不读取屏幕文字、通知或按键。\n已有其他 VPN 连接时保持原连接。");
        description.setTextSize(18); root.addView(description);
        status = new TextView(this); status.setTextSize(19); root.addView(status);
        pause = new Button(this);
        pause.setOnClickListener(view -> {
            boolean value = !getSharedPreferences("starter", MODE_PRIVATE).getBoolean("enabled", true);
            getSharedPreferences("starter", MODE_PRIVATE).edit().putBoolean("enabled", value).apply();
            updateStatus();
            if (value) FilterLauncher.request(this, "resume-button");
        }); root.addView(pause);
        Button launch = new Button(this); launch.setText("检查并启动过滤工具");
        launch.setOnClickListener(view -> {
            boolean ok = FilterLauncher.request(this, "manual-button");
            Toast.makeText(this, ok ? "已检查过滤连接" : "请先安装并配置过滤工具", Toast.LENGTH_LONG).show();
            updateStatus();
        }); root.addView(launch);
        Button settings = new Button(this); settings.setText("打开系统辅助功能设置");
        settings.setOnClickListener(view -> {
            try { startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)); }
            catch (ActivityNotFoundException error) {
                Toast.makeText(this, "这台电视未提供该设置入口，可通过配套配置流程启用。", Toast.LENGTH_LONG).show();
            }
        }); root.addView(settings);
        Button home = new Button(this); home.setText("返回小米桌面");
        home.setOnClickListener(view -> {
            startActivity(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME)); finish();
        }); root.addView(home);
        setContentView(root, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
    }
    @Override public void onResume() { super.onResume(); updateStatus(); }
    private void updateStatus() {
        String serviceList = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        ComponentName own = new ComponentName(this, StarterService.class);
        boolean active = false;
        if (serviceList != null) for (String value : serviceList.split(":")) {
            if (own.equals(ComponentName.unflattenFromString(value))) active = true;
        }
        boolean enabled = getSharedPreferences("starter", MODE_PRIVATE).getBoolean("enabled", true);
        pause.setText(enabled ? "暂停自动启动" : "恢复自动启动");
        status.setText("\n自动启动：" + (enabled ? "已开启" : "已暂停")
                + "\n系统辅助服务：" + (active ? "已启用" : "尚未启用")
                + "\nVPN 连接：" + (FilterLauncher.hasVpn(this) ? "已建立" : "未建立") + "\n");
    }
}
