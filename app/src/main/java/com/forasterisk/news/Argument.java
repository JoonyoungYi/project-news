package com.forasterisk.news;

public class Argument {

    /**
     * These Strings MUST NOT be changed!
     */
    public static final String PREFS = "user_info";
    public static final String PREFS_EMAIL_ID = "prefs_email_id";
    public static final String PREFS_SESSION_KEY = "prefs_session_key";
    public static final String PREFS_AUTO_KEY = "prefs_auto_key";
    public static final String PREFS_LOGIN_AUTH_API_REQUEST_TIME = "prefs_login_auth_api_request_time";
    public static final String PREFS_PORTAL_ID = "portal_id";
    public static final String PREFS_UUID = "prefs_uuid";
    public static final String PREFS_UNIV_ID = "prefs_univ_id";
    public static final String PREFS_ALARM_TIME_BREAKFAST = "prefs_alarm_time_breakfast";
    public static final String PREFS_ALARM_TIME_LUNCH = "prefs_alarm_time_launch";
    public static final String PREFS_ALARM_TIME_DINNER = "prefs_alarm_time_dinner";
    public static final String PREFS_LOG_ON = "prefs_log_on";
    public static final String PREFS_AD_ON = "prefs_ad_on";
    public static final String PREFS_CURRENT_VERSION = "prefs_current_version";
    public static final String PREFS_ADVERTISEMENT_LAST_UPDATE_DATE = "advertisement_last_update_date";
    public static final String PREFS_CAMPUS_ORDER = "prefs_campus_order";

    /**
     *
     */
    public static final int REQUEST_CODE_RECOVERD_FROM_FAIL_LOGIN = -3;
    public static final int REQUEST_CODE_RECOVERD = -2;
    public static final int REQUEST_CODE_SUCCESS = -1;
    public static final int REQUEST_CODE_UNEXPECTED = 0;
    public static final int REQUEST_CODE_FAIL_NETWORK = 1;
    public static final int REQUEST_CODE_FAIL_SERVER = 2;
    public static final int REQUEST_CODE_FAIL_SERVER_WITH_SERVER_STATUS_OK = 3;
    public static final int REQUEST_CODE_FAIL_SERVER_WITH_SERVER_STATUS_FAIL = 4;
    public static final int REQUEST_CODE_FAIL_SERVER_WITH_SERVER_STATUS_UNKNWON = 5;
    public static final int REQUEST_CODE_FAIL_COMMUNICATION = 6;
    public static final int REQUEST_CODE_FAIL_LOGIN = 7;
    public static final int REQUEST_CODE_FAIL_PARAMS = 8;
    public static final int REQUEST_CODE_FAIL_OLD_VERSION = 9;

    /**
     *
     */
    public static final int RESULT_CODE_REFRESH_BY_CHANING_UNIV = 1;
    public static final int RESULT_CODE_REFRESH_BY_LOGIN = 2;
    public static final int RESULT_CODE_REFRESH_BY_WRITE_COMMENT = 3;
    public static final int RESULT_CODE_REFRESH_BY_AD_STATE = 3;

}
