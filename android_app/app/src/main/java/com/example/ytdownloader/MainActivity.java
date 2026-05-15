package com.example.ytdownloader;

import android.app.Activity;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;
import android.webkit.DownloadListener;
import android.webkit.URLUtil;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final String PREFS_NAME = "yt_downloader_prefs";
    private static final String SERVER_URL_KEY = "server_url";
    private static final String DEFAULT_SERVER_URL = "http://10.0.2.2:8000/";

    private EditText serverUrlInput;
    private ProgressBar progressBar;
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(245, 245, 245));

        root.addView(createToolbar());

        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setIndeterminate(true);
        progressBar.setVisibility(View.GONE);
        root.addView(progressBar, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            6
        ));

        webView = new WebView(this);
        configureWebView();
        root.addView(webView, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            0,
            1
        ));

        setContentView(root);

        SharedPreferences preferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String serverUrl = preferences.getString(SERVER_URL_KEY, DEFAULT_SERVER_URL);
        serverUrlInput.setText(serverUrl);
        loadServerUrl(serverUrl);
    }

    private View createToolbar() {
        LinearLayout toolbar = new LinearLayout(this);
        toolbar.setOrientation(LinearLayout.VERTICAL);
        toolbar.setPadding(18, 16, 18, 16);
        toolbar.setBackgroundColor(Color.rgb(17, 17, 17));

        TextView title = new TextView(this);
        title.setText("YT Downloader");
        title.setTextColor(Color.WHITE);
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_VERTICAL);
        title.setTypeface(null, 1);
        toolbar.addView(title, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        LinearLayout formRow = new LinearLayout(this);
        formRow.setOrientation(LinearLayout.HORIZONTAL);
        formRow.setGravity(Gravity.CENTER_VERTICAL);
        formRow.setPadding(0, 14, 0, 0);

        serverUrlInput = new EditText(this);
        serverUrlInput.setSingleLine(true);
        serverUrlInput.setTextColor(Color.WHITE);
        serverUrlInput.setHintTextColor(Color.rgb(190, 190, 190));
        serverUrlInput.setHint(getString(R.string.server_hint));
        serverUrlInput.setTextSize(14);
        serverUrlInput.setSelectAllOnFocus(false);
        formRow.addView(serverUrlInput, new LinearLayout.LayoutParams(
            0,
            ViewGroup.LayoutParams.WRAP_CONTENT,
            1
        ));

        Button openButton = new Button(this);
        openButton.setText(getString(R.string.open));
        openButton.setTextColor(Color.WHITE);
        openButton.setBackgroundColor(Color.rgb(255, 0, 0));
        openButton.setOnClickListener(view -> loadServerUrl(serverUrlInput.getText().toString()));
        formRow.addView(openButton, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        toolbar.addView(formRow, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        return toolbar;
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();

                if ("youtube.com".equals(uri.getHost()) || "www.youtube.com".equals(uri.getHost()) || "youtu.be".equals(uri.getHost())) {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                    return true;
                }

                return false;
            }
        });

        webView.setDownloadListener(createDownloadListener());
    }

    private DownloadListener createDownloadListener() {
        return (url, userAgent, contentDisposition, mimeType, contentLength) -> {
            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
            String filename = URLUtil.guessFileName(url, contentDisposition, mimeType);

            request.addRequestHeader("User-Agent", userAgent);
            request.setTitle(filename);
            request.setDescription("YT Downloader file");
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename);

            DownloadManager downloadManager = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
            downloadManager.enqueue(request);

            Toast.makeText(this, "Downloading " + filename, Toast.LENGTH_LONG).show();
        };
    }

    private void loadServerUrl(String rawUrl) {
        String serverUrl = normalizeUrl(rawUrl);
        serverUrlInput.setText(serverUrl);
        getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .edit()
            .putString(SERVER_URL_KEY, serverUrl)
            .apply();

        hideKeyboard();
        webView.loadUrl(serverUrl);
    }

    private String normalizeUrl(String rawUrl) {
        String serverUrl = rawUrl == null ? "" : rawUrl.trim();

        if (serverUrl.isEmpty()) {
            serverUrl = DEFAULT_SERVER_URL;
        }

        if (!serverUrl.startsWith("http://") && !serverUrl.startsWith("https://")) {
            serverUrl = "http://" + serverUrl;
        }

        if (!serverUrl.endsWith("/")) {
            serverUrl = serverUrl + "/";
        }

        return serverUrl;
    }

    private void hideKeyboard() {
        InputMethodManager inputMethodManager = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);

        if (inputMethodManager != null) {
            inputMethodManager.hideSoftInputFromWindow(serverUrlInput.getWindowToken(), 0);
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
