package io.github.hankun1989.tvfilterstarter;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.util.Log;

final class FilterLauncher {
    static final String TAG = "TVFilterStarter";
    static final String TARGET = "com.github.metacubex.clash.meta";
    static boolean hasVpn(Context context) {
        ConnectivityManager manager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo info = manager == null ? null : manager.getNetworkInfo(ConnectivityManager.TYPE_VPN);
        return info != null && info.isConnected();
    }
    static boolean request(Context context, String reason) {
        if (hasVpn(context)) {
            Log.i(TAG, "VPN already connected; no launch needed (" + reason + ")");
            return true;
        }
        Intent intent = new Intent(TARGET + ".action.START_CLASH");
        intent.setComponent(new ComponentName(TARGET, "com.github.kr328.clash.ExternalControlActivity"));
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_NO_ANIMATION | Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS);
        try {
            context.startActivity(intent);
            Log.i(TAG, "Requested filter start (" + reason + ")");
            return true;
        } catch (RuntimeException error) {
            Log.e(TAG, "Cannot start installed filter", error);
            return false;
        }
    }
}
