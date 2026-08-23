package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.User;
import com.bookrecommender.app.utils.UserManager;

import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AuthActivity extends AppCompatActivity {
    private static final String TAG = "AuthActivity";
    private EditText etUsername, etPassword;
    private Button btnLogin, btnSignup;
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

        findViewById(R.id.btnSubmit).setOnClickListener(v -> submitForm());
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

        if (isLoginMode) {
            loginUser(username, password);
        } else {
            signupUser(username, password);
        }
    }

    private void loginUser(String username, String password) {
        User loginData = new User(username, null, password);
        apiService.loginUser(loginData).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    int userId = (int) response.body().get("user_id");
                    Log.d(TAG, "Login successful for user: " + userId);
                    userManager.saveUser(userId, username);
                    navigateToNextScreen();
                } else {
                    Log.e(TAG, "Login failed: " + response.code());
                    Toast.makeText(AuthActivity.this, "Invalid username or password", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(AuthActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void signupUser(String username, String password) {
        User newUser = new User(username, username + "@example.com", password);
        apiService.createUser(newUser).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    User createdUser = response.body();
                    Log.d(TAG, "Signup successful for user: " + createdUser.getId());
                    userManager.saveUser(createdUser.getId(), username);
                    navigateToNextScreen();
                } else {
                    Log.e(TAG, "Signup failed: " + response.code());
                    Toast.makeText(AuthActivity.this, "Username already exists", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<User> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(AuthActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void navigateToNextScreen() {
        if (userManager.isSetupDone()) {
            startActivity(new Intent(this, MainActivity.class));
        } else {
            startActivity(new Intent(this, SetupActivity.class));
        }
        finish();
    }
}