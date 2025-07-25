package com.example.ormapper;

import com.example.entity.UserEntity;
import java.util.List;

/**
 * User Entity OR Mapper
 * 実際のデータベースアクセスを担当
 */
public class UserORMapper {
    
    /**
     * ユーザー挿入
     */
    public void doInsert(UserEntity user) {
        // SQL実行: INSERT INTO users (name, email) VALUES (?, ?)
        System.out.println("SQL: INSERT INTO users VALUES(" + user.getName() + ", " + user.getEmail() + ")");
    }
    
    /**
     * ユーザー検索（ID指定）
     */
    public UserEntity select(Long id) {
        // SQL実行: SELECT * FROM users WHERE id = ?
        System.out.println("SQL: SELECT * FROM users WHERE id = " + id);
        
        UserEntity user = new UserEntity();
        user.setId(id);
        user.setName("Test User");
        user.setEmail("test@example.com");
        return user;
    }
    
    /**
     * ユーザー検索（全件）
     */
    public List<UserEntity> selectAll() {
        // SQL実行: SELECT * FROM users
        System.out.println("SQL: SELECT * FROM users");
        return List.of(new UserEntity());
    }
    
    /**
     * ユーザー検索（名前で検索）
     */
    public List<UserEntity> findByName(String name) {
        // SQL実行: SELECT * FROM users WHERE name LIKE ?
        System.out.println("SQL: SELECT * FROM users WHERE name LIKE '" + name + "%'");
        return List.of(new UserEntity());
    }
    
    /**
     * ユーザー更新
     */
    public void doUpdate(UserEntity user) {
        // SQL実行: UPDATE users SET name = ?, email = ? WHERE id = ?
        System.out.println("SQL: UPDATE users SET name = '" + user.getName() + "' WHERE id = " + user.getId());
    }
    
    /**
     * ユーザー削除
     */
    public void doDelete(Long id) {
        // SQL実行: DELETE FROM users WHERE id = ?
        System.out.println("SQL: DELETE FROM users WHERE id = " + id);
    }
    
    /**
     * ユーザー存在チェック
     */
    public boolean exists(Long id) {
        // SQL実行: SELECT COUNT(*) FROM users WHERE id = ?
        System.out.println("SQL: SELECT COUNT(*) FROM users WHERE id = " + id);
        return true;
    }
}