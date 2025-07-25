package com.example.batch;

import com.example.entity.UserEntity;
import com.example.entity.OrderEntity;
import com.example.mapper.UserEntityManager;
import com.example.ormapper.UserORMapper;
import com.example.ormapper.OrderORMapper;
import java.util.List;
import java.util.Date;

/**
 * User Data Migration Batch
 * バッチ処理 - Entity、EntityManager、ORMapperを直接使用
 */
public class UserDataMigrationBatch {
    
    private UserEntityManager userEntityManager;
    private UserORMapper userORMapper;
    private OrderORMapper orderORMapper;
    
    public UserDataMigrationBatch() {
        this.userEntityManager = new UserEntityManager();
        this.userORMapper = new UserORMapper();
        this.orderORMapper = new OrderORMapper();
    }
    
    /**
     * 旧システムからのユーザーデータ移行
     */
    public void migrateUsersFromLegacySystem() {
        System.out.println("Batch: Starting user migration from legacy system");
        
        // 1. 移行対象ユーザーを取得（模擬データ）
        List<LegacyUserData> legacyUsers = getLegacyUsers();
        
        int successCount = 0;
        int errorCount = 0;
        
        for (LegacyUserData legacyUser : legacyUsers) {
            try {
                // 2. 既存ユーザーチェック（重複回避）
                List<UserEntity> existingUsers = userORMapper.findByName(legacyUser.name);
                if (!existingUsers.isEmpty()) {
                    System.out.println("Batch: User already exists, skipping - " + legacyUser.name);
                    continue;
                }
                
                // 3. 新規ユーザー作成
                UserEntity newUser = new UserEntity();
                newUser.setName(legacyUser.name);
                newUser.setEmail(legacyUser.email);
                
                // EntityManagerではなく直接ORMapperを使用
                userORMapper.doInsert(newUser);
                successCount++;
                
                System.out.println("Batch: Migrated user - " + legacyUser.name);
                
            } catch (Exception e) {
                errorCount++;
                System.out.println("Batch: Failed to migrate user " + legacyUser.name + ": " + e.getMessage());
            }
        }
        
        System.out.println("Batch: Migration completed - Success: " + successCount + ", Errors: " + errorCount);
    }
    
    /**
     * 不要データの定期削除バッチ
     */
    public void cleanupOldData() {
        System.out.println("Batch: Starting old data cleanup");
        
        // 1. 全ユーザー取得
        List<UserEntity> allUsers = userEntityManager.findAll();
        
        int deletedUsers = 0;
        int deletedOrders = 0;
        
        for (UserEntity user : allUsers) {
            try {
                // 2. 古い注文を削除（例：1年以上前）
                List<OrderEntity> userOrders = orderORMapper.selectByUserId(user.getId());
                for (OrderEntity order : userOrders) {
                    // 実際の実装では日付チェックが必要
                    if (isOldOrder(order)) {
                        orderORMapper.doDelete(order.getOrderId());
                        deletedOrders++;
                    }
                }
                
                // 3. 注文のないユーザーを削除
                List<OrderEntity> remainingOrders = orderORMapper.selectByUserId(user.getId());
                if (remainingOrders.isEmpty() && isInactiveUser(user)) {
                    userORMapper.doDelete(user.getId());
                    deletedUsers++;
                    System.out.println("Batch: Deleted inactive user - " + user.getName());
                }
                
            } catch (Exception e) {
                System.out.println("Batch: Error processing user " + user.getId() + ": " + e.getMessage());
            }
        }
        
        System.out.println("Batch: Cleanup completed - Deleted users: " + deletedUsers + ", Deleted orders: " + deletedOrders);
    }
    
    /**
     * ユーザーデータの整合性チェック
     */
    public void validateDataIntegrity() {
        System.out.println("Batch: Starting data integrity validation");
        
        List<UserEntity> allUsers = userEntityManager.findAll();
        
        int invalidUsers = 0;
        int orphanedOrders = 0;
        
        for (UserEntity user : allUsers) {
            // 1. ユーザーデータの妥当性チェック
            if (user.getName() == null || user.getName().trim().isEmpty() ||
                user.getEmail() == null || !user.getEmail().contains("@")) {
                
                System.out.println("Batch: Invalid user data found - ID: " + user.getId());
                invalidUsers++;
                
                // データ修正または削除
                if (user.getName() == null) {
                    user.setName("Unknown_" + user.getId());
                }
                if (user.getEmail() == null || !user.getEmail().contains("@")) {
                    user.setEmail("invalid_" + user.getId() + "@example.com");
                }
                
                userEntityManager.update(user);
                System.out.println("Batch: Fixed user data - ID: " + user.getId());
            }
            
            // 2. 孤立した注文のチェック
            List<OrderEntity> userOrders = orderORMapper.selectByUserId(user.getId());
            for (OrderEntity order : userOrders) {
                if (!userORMapper.exists(order.getUserId())) {
                    orderORMapper.doDelete(order.getOrderId());
                    orphanedOrders++;
                    System.out.println("Batch: Deleted orphaned order - ID: " + order.getOrderId());
                }
            }
        }
        
        System.out.println("Batch: Validation completed - Fixed users: " + invalidUsers + ", Removed orphaned orders: " + orphanedOrders);
    }
    
    /**
     * 統計情報更新バッチ
     */
    public void updateStatistics() {
        System.out.println("Batch: Updating system statistics");
        
        // 全ユーザー数
        List<UserEntity> allUsers = userEntityManager.findAll();
        int totalUsers = allUsers.size();
        
        // アクティブユーザー数
        int activeUsers = 0;
        int totalOrders = 0;
        
        for (UserEntity user : allUsers) {
            List<OrderEntity> userOrders = orderORMapper.selectByUserId(user.getId());
            if (!userOrders.isEmpty()) {
                activeUsers++;
            }
            totalOrders += userOrders.size();
        }
        
        // 統計情報を保存（実際の実装では統計テーブルに保存）
        System.out.println("Batch: Statistics updated");
        System.out.println("  Total Users: " + totalUsers);
        System.out.println("  Active Users: " + activeUsers);
        System.out.println("  Total Orders: " + totalOrders);
        System.out.println("  Activity Rate: " + (activeUsers * 100.0 / totalUsers) + "%");
    }
    
    // ヘルパーメソッド
    private List<LegacyUserData> getLegacyUsers() {
        // 模擬的な旧システムデータ
        return List.of(
            new LegacyUserData("Legacy User 1", "legacy1@example.com"),
            new LegacyUserData("Legacy User 2", "legacy2@example.com")
        );
    }
    
    private boolean isOldOrder(OrderEntity order) {
        // 実際の実装では日付比較
        return true; // 簡略化
    }
    
    private boolean isInactiveUser(UserEntity user) {
        // 実際の実装では最終ログイン日時等を確認
        return true; // 簡略化
    }
    
    /**
     * 旧システムユーザーデータ
     */
    private static class LegacyUserData {
        public String name;
        public String email;
        
        public LegacyUserData(String name, String email) {
            this.name = name;
            this.email = email;
        }
    }
}