package com.example.util;

import com.example.entity.UserEntity;
import com.example.entity.OrderEntity;
import com.example.mapper.UserEntityManager;
import com.example.ormapper.UserORMapper;
import com.example.ormapper.OrderORMapper;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Data Access Utility
 * ユーティリティクラス - 様々なパターンでEntityとEntityManagerを使用
 */
public class DataAccessUtil {
    
    private static UserEntityManager userEntityManager = new UserEntityManager();
    private static UserORMapper userORMapper = new UserORMapper();
    private static OrderORMapper orderORMapper = new OrderORMapper();
    
    /**
     * ユーザー存在チェック（staticメソッド）
     */
    public static boolean checkUserExists(Long userId) {
        UserEntity user = userEntityManager.find(userId);
        return user != null;
    }
    
    /**
     * ユーザー情報の完全性チェック
     */
    public static ValidationResult validateUserData(UserEntity user) {
        ValidationResult result = new ValidationResult();
        
        if (user == null) {
            result.addError("User is null");
            return result;
        }
        
        if (user.getName() == null || user.getName().trim().isEmpty()) {
            result.addError("Name is required");
        }
        
        if (user.getEmail() == null || !user.getEmail().contains("@")) {
            result.addError("Valid email is required");
        }
        
        // 重複チェック（ORMapperで直接検索）
        List<UserEntity> duplicates = userORMapper.findByName(user.getName());
        if (!duplicates.isEmpty()) {
            result.addWarning("User with same name already exists");
        }
        
        return result;
    }
    
    /**
     * ユーザーの完全削除（関連データも含む）
     */
    public static void deleteUserCompletely(Long userId) {
        // 1. 関連注文を削除
        List<OrderEntity> orders = orderORMapper.selectByUserId(userId);
        for (OrderEntity order : orders) {
            orderORMapper.doDelete(order.getOrderId());
        }
        
        // 2. ユーザー削除
        userORMapper.doDelete(userId);
        
        System.out.println("DataAccessUtil: User " + userId + " and " + orders.size() + " related orders deleted");
    }
    
    /**
     * ユーザーデータのバックアップ作成
     */
    public static UserBackup createUserBackup(Long userId) {
        UserEntity user = userEntityManager.find(userId);
        if (user == null) {
            return null;
        }
        
        List<OrderEntity> orders = orderORMapper.selectByUserId(userId);
        
        UserBackup backup = new UserBackup();
        backup.user = user;
        backup.orders = orders;
        backup.backupDate = new java.util.Date();
        
        System.out.println("DataAccessUtil: Backup created for user " + userId + " with " + orders.size() + " orders");
        
        return backup;
    }
    
    /**
     * バックアップからユーザーデータを復元
     */
    public static void restoreUserFromBackup(UserBackup backup) {
        if (backup == null || backup.user == null) {
            throw new IllegalArgumentException("Invalid backup data");
        }
        
        // 1. ユーザー復元
        userORMapper.doInsert(backup.user);
        
        // 2. 注文復元
        for (OrderEntity order : backup.orders) {
            orderORMapper.doInsert(order);
        }
        
        System.out.println("DataAccessUtil: Restored user " + backup.user.getId() + 
                          " with " + backup.orders.size() + " orders from backup");
    }
    
    /**
     * システム統計情報取得
     */
    public static SystemStats getSystemStatistics() {
        List<UserEntity> allUsers = userEntityManager.findAll();
        
        SystemStats stats = new SystemStats();
        stats.totalUsers = allUsers.size();
        stats.totalOrders = 0;
        stats.activeUsers = 0;
        stats.userOrderCounts = new HashMap<>();
        
        for (UserEntity user : allUsers) {
            List<OrderEntity> userOrders = orderORMapper.selectByUserId(user.getId());
            int orderCount = userOrders.size();
            
            stats.totalOrders += orderCount;
            stats.userOrderCounts.put(user.getId(), orderCount);
            
            if (orderCount > 0) {
                stats.activeUsers++;
            }
        }
        
        return stats;
    }
    
    /**
     * 一括データ更新
     */
    public static void bulkUpdateUserEmails(String oldDomain, String newDomain) {
        List<UserEntity> allUsers = userEntityManager.findAll();
        
        int updatedCount = 0;
        
        for (UserEntity user : allUsers) {
            if (user.getEmail() != null && user.getEmail().contains(oldDomain)) {
                String newEmail = user.getEmail().replace(oldDomain, newDomain);
                user.setEmail(newEmail);
                
                userORMapper.doUpdate(user);
                updatedCount++;
            }
        }
        
        System.out.println("DataAccessUtil: Updated " + updatedCount + " user emails from " + 
                          oldDomain + " to " + newDomain);
    }
    
    // データクラス
    public static class ValidationResult {
        private List<String> errors = new java.util.ArrayList<>();
        private List<String> warnings = new java.util.ArrayList<>();
        
        public void addError(String error) { errors.add(error); }
        public void addWarning(String warning) { warnings.add(warning); }
        public boolean hasErrors() { return !errors.isEmpty(); }
        public List<String> getErrors() { return errors; }
        public List<String> getWarnings() { return warnings; }
    }
    
    public static class UserBackup {
        public UserEntity user;
        public List<OrderEntity> orders;
        public java.util.Date backupDate;
    }
    
    public static class SystemStats {
        public int totalUsers;
        public int totalOrders;
        public int activeUsers;
        public Map<Long, Integer> userOrderCounts;
    }
}