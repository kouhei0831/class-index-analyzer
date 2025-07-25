package com.example.mapper;

import com.example.entity.UserEntity;
import com.example.ormapper.UserORMapper;
import java.util.List;

/**
 * User Entity Manager
 * ビジネスロジックとOR Mapperの橋渡し
 */
public class UserEntityManager {
    
    private UserORMapper userORMapper;
    
    public UserEntityManager() {
        this.userORMapper = new UserORMapper();
    }
    
    /**
     * ユーザー作成
     */
    public void insert(UserEntity user) {
        // バリデーション
        if (user.getName() == null || user.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("User name is required");
        }
        
        // OR Mapperに委譲
        userORMapper.doInsert(user);
        System.out.println("Manager: User inserted successfully");
    }
    
    /**
     * ユーザー検索
     */
    public UserEntity find(Long id) {
        if (id == null || id <= 0) {
            throw new IllegalArgumentException("Valid user ID is required");
        }
        
        return userORMapper.select(id);
    }
    
    /**
     * 全ユーザー取得
     */
    public List<UserEntity> findAll() {
        return userORMapper.selectAll();
    }
    
    /**
     * 名前でユーザー検索
     */
    public List<UserEntity> searchByName(String name) {
        if (name == null || name.trim().isEmpty()) {
            return List.of();
        }
        
        return userORMapper.findByName(name);
    }
    
    /**
     * ユーザー更新
     */
    public void update(UserEntity user) {
        if (user.getId() == null) {
            throw new IllegalArgumentException("User ID is required for update");
        }
        
        // 存在チェック
        if (!userORMapper.exists(user.getId())) {
            throw new RuntimeException("User not found: " + user.getId());
        }
        
        userORMapper.doUpdate(user);
        System.out.println("Manager: User updated successfully");
    }
    
    /**
     * ユーザー削除
     */
    public void delete(Long id) {
        if (id == null || id <= 0) {
            throw new IllegalArgumentException("Valid user ID is required");
        }
        
        // 存在チェック
        if (!userORMapper.exists(id)) {
            throw new RuntimeException("User not found: " + id);
        }
        
        userORMapper.doDelete(id);
        System.out.println("Manager: User deleted successfully");
    }
}