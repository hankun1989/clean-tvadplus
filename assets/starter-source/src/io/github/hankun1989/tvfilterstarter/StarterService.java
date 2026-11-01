package io.github.hankun1989.tvfilterstarter;

import android.accessibilityservice.AccessibilityService;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

public final class StarterService extends AccessibilityService {
    private final Handler handler = new Handler(Looper.getMainLooper());
    private long lastAttempt = -30000;

    @Override protected void onServiceConnected() {
        super.onServiceConnected();
        Log.i(FilterLauncher.TAG, "Accessibility service connected; uptime=" + SystemClock.elapsedRealtime());
        handler.postDelayed(() -> ensure("service-connected"), 1500);
        handler.postDelayed(() -> ensure("startup-retry"), 10000);
        handler.postDelayed(() -> ensure("startup-retry"), 30000);
        handler.postDelayed(() -> ensure("startup-retry"), 60000);
        handler.postDelayed(() -> ensure("startup-retry"), 120000);
    }

    private void ensure(String reason) {
        if (!getSharedPreferences("starter", MODE_PRIVATE).getBoolean("enabled", true)) return;
        if (FilterLauncher.hasVpn(this)) return;
        long now = SystemClock.elapsedRealtime();
        if (now - lastAttempt < 5000) return;
        lastAttempt = now;
        FilterLauncher.request(this, reason);
    }

    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        // Never inspect event text, source nodes, key events or notification data.
        if (event != null && event.getEventType() == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
                && "com.mitv.tvhome".contentEquals(event.getPackageName() == null ? "" : event.getPackageName())) {
            handler.postDelayed(() -> ensure("stock-home-window"), 1000);
        }
    }

    @Override public void onInterrupt() { }
    @Override public void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
}
