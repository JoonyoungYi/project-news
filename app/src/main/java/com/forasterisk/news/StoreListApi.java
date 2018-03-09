package com.forasterisk.news;

import android.app.Application;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;

public class StoreListApi extends ApiBase {
    public final static String API_NAME = "StoreListApi";
    public final static String PARAM_UNIV_ID = "univ_id";

    /**
     *
     */
    private ArrayList<Article> stores = null;

    /**
     * Init
     */
    public StoreListApi(Application application, HashMap<String, String> params) {
        super(application, params);

        Log.d(API_NAME, "StoreListApi Started!");

        /**
         * Check Fail Parameters
         */
        if (isFailParams()) {
            return;
        }

        /**
         * Handle Response
         */
        String response = getResponseFromRemote();
        Log.d(API_NAME
                , "hi333");

        /**
         *
         */
        this.stores = getStoresFromResponse(response);
        this.request_code = Argument.REQUEST_CODE_SUCCESS;
    }

    /**
     * @return
     */
    public static HashMap<String, String> createParams(int univ_id) {
        HashMap<String, String> params = new HashMap<>();
        params.put(PARAM_UNIV_ID, "" + univ_id);
        return params;
    }

    /**
     * @return
     */
    protected String getResponseFromRemote() {
        return super.getResponseFromRemote("/0.json", "GET", "https");
    }

    /**
     * @return
     */
    public ArrayList<Article> getResult() {
        return this.stores;
    }

    /**
     * @return
     */
    private ArrayList<Article> getStoresFromResponse(String response) {

        /**
         *
         */
        if (response == null) {
            Log.d(API_NAME, "hi3");
            return null;
        }

        /**
         *
         */
        ArrayList<Article> stores = new ArrayList<Article>();
        try {
            JSONObject jsonObj = new JSONObject(response);
            JSONArray jsonArray = jsonObj.getJSONArray("articles");
            Log.d(API_NAME, "hi2");

            for (int i = 0; i < jsonArray.length(); i++) {

                Log.d(API_NAME, "hi");
                JSONObject obj = jsonArray.getJSONObject(i);
                Article store = new Article();

                if (!obj.isNull("title")) {
                    String title = obj.getString("title");
                    Log.d(API_NAME, " title -> " + title);
                    store.setTitle(title);
                }

                if (!obj.isNull("press")) {
                    String title = obj.getString("press");
                    store.setPress(title);
                }

                if (!obj.isNull("img_url")) {
                    String title = obj.getString("img_url");
                    store.setImg_url(title);
                }
                if (!obj.isNull("sentence")) {
                    String location = obj.getString("sentence");
                    store.setSentence(location);
                    Log.d(API_NAME, " sentence -> " + location);
                }
                if (!obj.isNull("url")) {
                    String title = obj.getString("url");
                    store.setUrl(title);
                }

                stores.add(store);
            }


        } catch (Exception e) {
            e.printStackTrace();
            stores = null;
        }

        return stores;
    }


}
