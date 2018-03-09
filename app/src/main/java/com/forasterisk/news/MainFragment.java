package com.forasterisk.news;

import android.app.Activity;
import android.content.Intent;
import android.content.res.Resources;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;

import com.squareup.picasso.Picasso;

import java.util.ArrayList;

/**
 * Created by yearnning on 15. 6. 11..
 */
public class MainFragment extends Fragment {

    private static final String TAG = "MainFragment";

    /**
     * The fragment argument representing the section number for this
     * fragment.
     */
    private static final String ARG_SECTION_NUMBER = "section_number";

    private ListView mLv;

    private LvAdapter mLvAdapter;


    /**
     *
     */
    private ListApiTask mListApiTask = null;
    private LoadingViewManager mLoadingViewManager;

    /**
     * Returns a new instance of this fragment for the given section
     * number.
     */
    public static MainFragment newInstance(int sectionNumber) {
        MainFragment fragment = new MainFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_SECTION_NUMBER, sectionNumber);
        fragment.setArguments(args);
        return fragment;
    }

    public MainFragment() {
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_main, container, false);

        View mProgressBar = rootView.findViewById(R.id.progress_bar);
        mLv = (ListView) rootView.findViewById(R.id.lv);
        mLoadingViewManager = new LoadingViewManager(getActivity(), mProgressBar, mLv, null);

        mLv.addHeaderView(new View(getActivity()));
        mLv.addFooterView(new View(getActivity()));

        /*
         * ListView Setting
		 */
        ArrayList<Article> stores = new ArrayList<>();
        mLvAdapter = new LvAdapter(getActivity(), R.layout.main_fragment_lv,
                stores);
        mLv.setAdapter(mLvAdapter);

        /*

         */
        requestRefresh(true);

        return rootView;
    }

    /**
     *
     */
    public void requestRefresh(boolean init) {

        if (init)
            mLoadingViewManager.init();

        if (mListApiTask != null)
            return;

        mListApiTask = new ListApiTask();
        mListApiTask.execute(1);

    }


    /**
     * ListView Apdater Setting
     */
    private class LvAdapter extends ArrayAdapter<Article> {
        private static final String TAG = "MainFragment LvAdapter";
        public ArrayList<Article> stores;
        private ViewHolder viewHolder = null;
        private int textViewResourceId;


        private Resources r;
        private MainActivity activity;

        public LvAdapter(Activity context, int textViewResourceId,
                         ArrayList<Article> stores) {
            super(context, textViewResourceId, stores);

            this.textViewResourceId = textViewResourceId;
            this.stores = stores;
            this.activity = (MainActivity) getActivity();
            this.r = getResources();
        }

        @Override
        public boolean hasStableIds() {
            return true;
        }

        @Override
        public int getCount() {
            return stores.size();
        }

        @Override
        public Article getItem(int position) {
            return stores.get(position);
        }

        @Override
        public long getItemId(int position) {
            return position;
        }

        @Override
        public View getView(final int position, View convertView, ViewGroup parent) {

			/*
             * UI Initiailizing : View Holder
			 */

            if (convertView == null) {
                convertView = getActivity().getLayoutInflater()
                        .inflate(textViewResourceId, null);

                viewHolder = new ViewHolder();
                viewHolder.mIconIv = (ImageView) convertView.findViewById(R.id.icon_iv);
                viewHolder.mTitleTv = (TextView) convertView.findViewById(R.id.title_tv);
                viewHolder.mSentenceTv = (TextView) convertView.findViewById(R.id.sentence_tv);
                viewHolder.mPressTv = (TextView) convertView.findViewById(R.id.press_tv);
                viewHolder.mCardView = convertView.findViewById(R.id.card_view);
                convertView.setTag(viewHolder);

            } else {
                viewHolder = (ViewHolder) convertView.getTag();
            }

            final Article store = this.getItem(position);

			/*
             * Data Import and export
			 */

            //
            viewHolder.mTitleTv.setText(store.getTitle());
            viewHolder.mSentenceTv.setText(store.getSentence());
            viewHolder.mPressTv.setText(store.getPress());

            /**
             *
             */
            if (store.getImg_url() != null) {
                Picasso.with(getActivity()).load(store.getImg_url())
                        .placeholder(R.color.bab_grey).into(viewHolder.mIconIv);
                viewHolder.mIconIv.setVisibility(View.VISIBLE);
            } else {
                viewHolder.mIconIv.setVisibility(View.GONE);
            }

            viewHolder.mCardView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Intent i = new Intent(Intent.ACTION_VIEW,
                            Uri.parse(store.getUrl()));
                    startActivity(i);
                }
            });


            return convertView;
        }

        @Override
        public boolean isEnabled(int position) {

            return false;
        }

        private class ViewHolder {

            ImageView mIconIv;

            TextView mTitleTv;
            TextView mSentenceTv;
            TextView mPressTv;
            View mCardView;
        }
    }

    /**
     * Represents an asynchronous login/registration task used to authenticate
     * the user.
     */
    public class ListApiTask extends AsyncTask<Integer, Void, ArrayList<Article>> {
        private int store_type = -1;
        private int request_code = Argument.REQUEST_CODE_UNEXPECTED;

        @Override
        protected void onPreExecute() {
            mLoadingViewManager.show(true);
        }

        @Override
        protected ArrayList<Article> doInBackground(Integer... sort) {
            ArrayList<Article> stores = null;
            store_type = sort[0];

            try {


                StoreListApi storeListApi = new StoreListApi(getActivity().getApplication(),
                        StoreListApi.createParams(0));

                stores = storeListApi.getResult();
                request_code = storeListApi.getRequestCode();

            } catch (Exception e) {
                e.printStackTrace();
            }

            return stores;
        }


        @Override
        protected void onPostExecute(ArrayList<Article> stores) {
            ApiBase.showToastMsg(getActivity(), request_code);
            //Log.d(TAG, "store_type -> " + store_type + ", request_code -> " + request_code);

            /**
             *
             */
            mLvAdapter.stores.clear();


            /**
             *
             */
            if (stores == null) {

                /* if (request_code == Argument.REQUEST_CODE_FAIL_LOGIN && store_type == 100) {
                    mErrorViewManager.show(true, ErrorViewManager.Type.LOGIN_FOR_FAVORITE);

                } else {
                    mErrorViewManager.show(true, ErrorViewManager.Type.FAIL_LOADING_STORES);
                } */

            } else {
                Log.d(TAG, "stores_len -> " + stores.size());
                mLvAdapter.stores.addAll(stores);
            }

            /**
             *
             *//*
            if (stores == null || stores.size() == 0) {
                mLvFooter.setVisibility(View.GONE);
            } else {
                mLvFooter.setVisibility(View.VISIBLE);
            }

            /**
             *
             */
            mLvAdapter.notifyDataSetChanged();

            /**
             *
             */
            mLoadingViewManager.show(false);

            /**
             *
             */
            mListApiTask = null;
        }

        @Override
        protected void onCancelled() {
            super.onCancelled();

            /**
             *
             */
            mLoadingViewManager.show(false);

            /**
             *
             */
            mListApiTask = null;
        }
    }
}
