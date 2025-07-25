package com.example.controller;

import com.example.entity.UserEntity;
import com.example.mapper.UserEntityManager;
import com.example.UserService;
import java.util.List;

/**
 * User Controller
 * REST APIエンドポイント - EntityとEntityManagerを直接import
 */
public class UserController {
    
    private UserEntityManager userEntityManager;
    private UserService userService;
    
    public UserController() {
        this.userEntityManager = new UserEntityManager();
        this.userService = new UserService();
    }
    
    /**
     * ユーザー作成API
     * POST /api/users
     */
    public UserEntity createUser(String name, String email) {
        // バリデーション
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Name is required");
        }
        
        // 直接EntityManagerを使用するパターン
        UserEntity user = new UserEntity();
        user.setName(name);
        user.setEmail(email);
        
        userEntityManager.insert(user);
        System.out.println("Controller: User created via EntityManager");
        
        return user;
    }
    
    /**
     * ユーザー取得API
     * GET /api/users/{id}
     */
    public UserEntity getUser(Long id) {
        // EntityManagerから直接取得
        UserEntity user = userEntityManager.find(id);
        if (user == null) {
            throw new RuntimeException("User not found: " + id);
        }
        return user;
    }
    
    /**
     * 全ユーザー取得API
     * GET /api/users
     */
    public List<UserEntity> getAllUsers() {
        // EntityManagerから全件取得
        return userEntityManager.findAll();
    }
    
    /**
     * ユーザー更新API
     * PUT /api/users/{id}
     */
    public UserEntity updateUser(Long id, String name, String email) {
        // 既存ユーザー取得
        UserEntity user = userEntityManager.find(id);
        if (user == null) {
            throw new RuntimeException("User not found: " + id);
        }
        
        // 更新
        user.setName(name);
        user.setEmail(email);
        
        userEntityManager.update(user);
        System.out.println("Controller: User updated via EntityManager");
        
        return user;
    }
    
    /**
     * ユーザー削除API
     * DELETE /api/users/{id}
     */
    public void deleteUser(Long id) {
        // EntityManagerで削除
        userEntityManager.delete(id);
        System.out.println("Controller: User deleted via EntityManager");
    }
    
    /**
     * ユーザー検索API (Serviceレイヤー経由)
     * GET /api/users/search?name={name}
     */
    public List<UserEntity> searchUsers(String name) {
        // Serviceレイヤーを使用するパターン
        return userService.searchUsersByName(name);
    }
    
    /**
     * ユーザー一括作成API
     * POST /api/users/batch
     */
    public void createUsersBatch(List<String> names, List<String> emails) {
        if (names.size() != emails.size()) {
            throw new IllegalArgumentException("Names and emails must have same length");
        }
        
        for (int i = 0; i < names.size(); i++) {
            UserEntity user = new UserEntity();
            user.setName(names.get(i));
            user.setEmail(emails.get(i));
            
            // EntityManagerで直接挿入
            userEntityManager.insert(user);
        }
        
        System.out.println("Controller: Batch users created - " + names.size() + " users");
    }
}