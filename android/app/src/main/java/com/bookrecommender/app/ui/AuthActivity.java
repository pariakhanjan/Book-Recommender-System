package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.LoginResponse;
import com.bookrecommender.app.models.User;
import com.bookrecommender.app.models.UserLogin;
import com.bookrecommender.app.models.UserRegister;
import com.bookrecommender.app.utils.UserManager;
import com.bookrecommender.app.models.UserPreferences;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Activity handling user authentication (Login and Sign Up).
 * Manages UI state transitions and communicates with the backend for auth.
 */
public class AuthActivity extends AppCompatActivity {
    private static final String TAG = "AuthActivity";

    private android.widget.EditText etUsername, etPassword;
    private Button btnLogin, btnSignup, btnSubmit;
    private ProgressBar progressBar;
    private TextView tvTitle;

    private ApiInterface apiService;
    private UserManager userManager;
    private boolean isLoginMode = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_auth);

        apiService = RetrofitClient.getClient().create(ApiInterface.class);
        userManager = new UserManager(this);

        if (userManager.isLoggedIn()) {
            navigateToNextScreen();
            return;
        }

        initViews();
        setupListeners();
    }

    private void initViews() {
        etUsername = findViewById(R.id.etUsername);
        etPassword = findViewById(R.id.etPassword);
        btnLogin = findViewById(R.id.btnLogin);
        btnSignup = findViewById(R.id.btnSignup);
        btnSubmit = findViewById(R.id.btnSubmit);
        progressBar = findViewById(R.id.progressBar);
        tvTitle = findViewById(R.id.tvTitle);
    }

    private void setupListeners() {
        btnLogin.setOnClickListener(v -> {
            isLoginMode = true;
            tvTitle.setText("Login");
            btnLogin.setBackgroundColor(getColor(R.color.primary_purple));
            btnSignup.setBackgroundColor(getColor(R.color.primary_blue));
        });

        btnSignup.setOnClickListener(v -> {
            isLoginMode = false;
            tvTitle.setText("Sign Up");
            btnSignup.setBackgroundColor(getColor(R.color.primary_purple));
            btnLogin.setBackgroundColor(getColor(R.color.primary_blue));
        });

        btnSubmit.setOnClickListener(v -> submitForm());
    }

    private void submitForm() {
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (username.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Username and password are required", Toast.LENGTH_SHORT).show();
            return;
        }

        if (username.length() < 3) {
            Toast.makeText(this, "Username must be at least 3 characters", Toast.LENGTH_SHORT).show();
            return;
        }

        if (password.length() < 6) {
            Toast.makeText(this, "Password must be at least 6 characters", Toast.LENGTH_SHORT).show();
            return;
        }

        progressBar.setVisibility(View.VISIBLE);
        btnSubmit.setEnabled(false);

        if (isLoginMode) {
            loginUser(username, password);
        } else {
            signupUser(username, password);
        }
    }

    private void loginUser(String username, String password) {
        UserLogin loginData = new UserLogin(username, password);

        apiService.loginUser(loginData).enqueue(new Callback<LoginResponse>() {
            @Override
            public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
                progressBar.setVisibility(View.GONE);
                btnSubmit.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    LoginResponse data = response.body();
                    Log.d(TAG, "Login successful for user ID: " + data.getUserId());
                    userManager.saveUser(data.getUserId(), data.getUsername());
                    navigateToNextScreen();
                } else {
                    Log.e(TAG, "Login failed: " + response.code());
                    Toast.makeText(AuthActivity.this, "Invalid username or password", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<LoginResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnSubmit.setEnabled(true);
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(AuthActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void signupUser(String username, String password) {
        UserRegister newUser = new UserRegister(username, password);

        apiService.createUser(newUser).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                progressBar.setVisibility(View.GONE);
                btnSubmit.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    User createdUser = response.body();
                    Log.d(TAG, "Signup successful for user ID: " + createdUser.getId());
                    userManager.saveUser(createdUser.getId(), createdUser.getUsername());
                    navigateToNextScreen();
                } else {
                    Log.e(TAG, "Signup failed: " + response.code());
                    Toast.makeText(AuthActivity.this, "Username already exists", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<User> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnSubmit.setEnabled(true);
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(AuthActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void navigateToNextScreen() {
        int userId = userManager.getUserId();
        apiService.getUserPreferences(userId).enqueue(new Callback<UserPreferences>() {
            @Override
            public void onResponse(Call<UserPreferences> call, Response<UserPreferences> response) {
                if (response.isSuccessful() && response.body() != null) {
                    UserPreferences prefs = response.body();
                    if (prefs.getPreferredLanguages() != null && !prefs.getPreferredLanguages().isEmpty()) {
                        userManager.markSetupDone();
                        Intent intent = new Intent(AuthActivity.this, MainActivity.class);
                        startActivity(intent);
                        finish();
                    } else {
                        Intent intent = new Intent(AuthActivity.this, PreferenceActivity.class);
                        startActivity(intent);
                        finish();
                    }
                } else {
                    Intent intent = new Intent(AuthActivity.this, PreferenceActivity.class);
                    startActivity(intent);
                    finish();
                }
            }

            @Override
            public void onFailure(Call<UserPreferences> call, Throwable t) {
                Log.e(TAG, "Failed to fetch preferences: " + t.getMessage());
                Intent intent = new Intent(AuthActivity.this, PreferenceActivity.class);
                startActivity(intent);
                finish();
            }
        });
    }
}