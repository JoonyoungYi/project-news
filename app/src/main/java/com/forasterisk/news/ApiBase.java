package com.forasterisk.news;

import android.app.Activity;
import android.content.Context;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.HashMap;
import java.util.Iterator;

public class ApiBase {
    public final static String API_NAME = "ApiBase";

    /**
     *
     */
    protected Context mContext = null;
    protected HashMap<String, String> mParams = null;
    protected int request_code = Argument.REQUEST_CODE_UNEXPECTED;

    /**
     * Constructor
     *
     * @param context
     * @param params
     */
    public ApiBase(Context context, HashMap<String, String> params) {
        this.mContext = context;
        this.mParams = params;
    }

    /**
     * @param request_code
     */
    public static void showToastMsg(Activity activity, int request_code) {

        /**
         *
         */
        if (activity == null)
            return;

        /**
         *
         */
        if (request_code == Argument.REQUEST_CODE_FAIL_NETWORK) {
            Toast.makeText(activity, "인터넷 연결이 불안정합니다. 잠시 후, 다시 시도해 주세요.", Toast.LENGTH_LONG).show();

        } else if (request_code == Argument.REQUEST_CODE_UNEXPECTED) {
            Toast.makeText(activity, "알 수 없는 오류가 발생했습니다. 잠시 후, 다시 시도해 주세요.", Toast.LENGTH_LONG).show();

        } else if (request_code == Argument.REQUEST_CODE_FAIL_COMMUNICATION) {
            Toast.makeText(activity, "서버와의 통신에 오류가 발생했습니다. 잠시 후, 다시 시도해 주세요.", Toast.LENGTH_LONG).show();

        } else if (request_code == Argument.REQUEST_CODE_FAIL_SERVER) {
            Toast.makeText(activity, "서버가 응답하지 않습니다. 잠시 후, 다시 시도해 주세요.", Toast.LENGTH_LONG).show();

        } else if (request_code == Argument.REQUEST_CODE_FAIL_SERVER_WITH_SERVER_STATUS_OK) {
            Toast.makeText(activity, "요청이 서버로 전송되지 않았습니다. 잠시 후, 다시 시도해 주세요.", Toast.LENGTH_LONG).show();

        } else if (request_code == Argument.REQUEST_CODE_FAIL_SERVER_WITH_SERVER_STATUS_UNKNWON) {
            Toast.makeText(activity, "서버의 응답여부를 알 수 없습니다. 잠시 후, 다시 시도해 주세요.", Toast.LENGTH_LONG).show();

        } else if (request_code == Argument.REQUEST_CODE_FAIL_OLD_VERSION) {
            Toast.makeText(activity, "너무 오래된 버전을 사용하고 계십니다. 업데이트를 위해 플레이스토어로 이동합니다.", Toast.LENGTH_LONG).show();

        }
    }

    /**
     * @return
     */
    public int getRequestCode() {
        return this.request_code;
    }

    /**
     * @return
     */
    protected boolean isFailNetwork() {

        if (!RequestManager.isNetworkConnected(mContext)) {
            this.request_code = Argument.REQUEST_CODE_FAIL_NETWORK;
            return true;
        }

        return false;
    }

    /**
     * @return
     */
    protected boolean isFailParams() {
        return false;
    }

    /**
     * @param api_url
     * @param method
     * @param type
     * @return
     */
    protected String getResponseFromRemote(String api_url, String method, String type) {

        if (isFailNetwork()) {
            return null;
        }

        /**
         * Init Request Manager
         */
        RequestManager rm = new RequestManager(api_url, method, type);

        /**
         * Add Session Key in Header
         */
        // rm.addHeader("sessionkey", PreferenceManager.getSessionKeyInPrefs(mContext));

        /**
         * Add Body Parameters
         */
        Iterator<String> iter = mParams.keySet().iterator();
        while (iter.hasNext()) {
            String key = iter.next();
            rm.addBodyValue(key, mParams.get(key));
        }

        /**
         * Do Request and get Response
         */
        rm.doRequest();
        String response = rm.getResponse_body();

        /**
         * return response
         */
        return response;
    }

    /**
     * @param response
     * @return
     */
    private boolean isFailServer(String response) {
        if (response == null || response.equals("")) {
            this.request_code = Argument.REQUEST_CODE_FAIL_SERVER;
            return true;
        }
        return false;
    }

    /**
     * @param response
     * @return
     */
    private boolean isFailCommunication(String response) {

        try {
            return true;

        } catch (Exception e) {
            e.printStackTrace();

        }
        this.request_code = Argument.REQUEST_CODE_FAIL_COMMUNICATION;
        return true;
    }

    /**
     * @return
     */
    protected String getCacheFileName() {

        String fileName = API_NAME;

        Iterator<String> iter = mParams.keySet().iterator();
        while (iter.hasNext()) {
            String key = iter.next();
            fileName += "__" + key + "__" + mParams.get(key);
        }

        return fileName;
    }

    /**
     * @param response
     */
    protected void saveResponseToCache(String response) {

        try {
            FileOutputStream outputStream = new FileOutputStream(new File(mContext.getCacheDir(), getCacheFileName()));
            outputStream.write(response.getBytes());
            outputStream.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * @return
     */
    protected String getResponseFromCache() {
        try {
            FileInputStream fin = new FileInputStream(new File(mContext.getCacheDir(), getCacheFileName()));

            StringBuilder sb = new StringBuilder("");
            byte[] buffer = new byte[1024];
            int c;
            while ((c = fin.read(buffer)) != -1) {
                sb.append(new String(buffer, 0, c));
            }
            fin.close();
            return sb.toString();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }

    /**
     * @param context
     */
    public static void cleanCacheDir(Context context) {

        File[] files = context.getCacheDir().listFiles();
        for (File file : files) {
            file.delete();
        }
    }

}
