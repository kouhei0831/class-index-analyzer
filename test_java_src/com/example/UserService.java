package com.example;

import com.example.entity.UserEntity;
import com.example.mapper.UserEntityManager;
import java.util.List;

/**
 * User Service
 * ユーザー関連のビジネスロジック
 */
public class UserService {
    
    private UserEntityManager userManager;
    
    public UserService() {
        this.userManager = new UserEntityManager();
    }
    
    /**
     * 新規ユーザー作成
     */
    public UserEntity createUser(String name, String email) {
        // バリデーション
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Name is required");
        }
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Valid email is required");
        }
        
        UserEntity user = new UserEntity();
        user.setName(name);
        user.setEmail(email);
        
        userManager.insert(user);
        System.out.println("Service: User created - " + name);
        
        return user;
    }
    
    /**
     * ユーザー検索（ID指定）
     */
    public UserEntity findUserById(Long id) {
        UserEntity user = userManager.find(id);
        if (user == null) {
            throw new RuntimeException("User not found: " + id);
        }
        return user;
    }
    
    /**
     * 全ユーザー取得
     */
    public List<UserEntity> getAllUsers() {
        return userManager.findAll();
    }
    
    /**
     * ユーザー検索（名前）
     */
    public List<UserEntity> searchUsersByName(String name) {
        return userManager.searchByName(name);
    }
    
    /**
     * ユーザー情報更新
     */
    public void updateUser(UserEntity user) {
        if (user == null) {
            throw new IllegalArgumentException("User cannot be null");
        }
        
        userManager.update(user);
        System.out.println("Service: User updated - " + user.getName());
    }
    
    /**
     * ユーザー削除
     */
    public void deleteUser(Long id) {
        userManager.delete(id);
        System.out.println("Service: User deleted - " + id);
    }
    
    /**
     * ユーザー一括削除
     */
    public void deleteAllUsers() {
        List<UserEntity> users = userManager.findAll();
        for (UserEntity user : users) {
            userManager.delete(user.getId());
        }
        System.out.println("Service: All users deleted");
    }
}