package com.bookrecommender.app.api;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import java.util.concurrent.TimeUnit;

/**
 * Singleton class responsible for configuring and providing the Retrofit instance.
 */
public class RetrofitClient {
    private static Retrofit retrofit = null;

    /**
     * Gets the singleton Retrofit instance with configured timeouts and logging.
     * @return Configured Retrofit instance.
     */
    public static Retrofit getClient() {
        if (retrofit == null) {
            String baseUrl = com.bookrecommender.app.BuildConfig.API_BASE_URL;

            if (!baseUrl.endsWith("/")) {
                baseUrl += "/";
            }

            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);
            OkHttpClient.Builder httpClient = new OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .writeTimeout(30, TimeUnit.SECONDS) // ✅ Added to prevent upload timeouts
                    .addInterceptor(logging);
            retrofit = new Retrofit.Builder()
                    .baseUrl(baseUrl)
                    .addConverterFactory(GsonConverterFactory.create())
                    .client(httpClient.build())
                    .build();
        }
        return retrofit;
    }
}