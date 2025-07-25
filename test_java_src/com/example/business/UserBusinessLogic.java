package com.example.business;

import com.example.entity.UserEntity;
import com.example.entity.OrderEntity;
import com.example.mapper.UserEntityManager;
import com.example.service.OrderService;
import java.util.List;
import java.util.Date;

/**
 * User Business Logic
 * 複雑なビジネスロジック - Entity、EntityManagerを含む複合処理
 */
public class UserBusinessLogic {
    
    private UserEntityManager userEntityManager;
    private OrderService orderService;
    
    public UserBusinessLogic() {
        this.userEntityManager = new UserEntityManager();
        this.orderService = new OrderService();
    }
    
    /**
     * ユーザー登録 + 初回特典処理
     */
    public UserEntity registerUserWithWelcomeBonus(String name, String email) {
        // 1. ユーザー作成
        UserEntity user = new UserEntity();
        user.setName(name);
        user.setEmail(email);
        
        userEntityManager.insert(user);
        System.out.println("BusinessLogic: User registered - " + name);
        
        // 2. 初回特典注文の自動作成
        try {
            orderService.createOrder(user.getId(), "Welcome Bonus", 1, new java.math.BigDecimal("0.00"));
            System.out.println("BusinessLogic: Welcome bonus created");
        } catch (Exception e) {
            System.out.println("BusinessLogic: Failed to create welcome bonus: " + e.getMessage());
        }
        
        return user;
    }
    
    /**
     * ユーザー退会処理（関連データ一括削除）
     */
    public void withdrawUser(Long userId) {
        // 1. ユーザー存在確認
        UserEntity user = userEntityManager.find(userId);
        if (user == null) {
            throw new RuntimeException("User not found: " + userId);
        }
        
        // 2. 関連注文を全削除
        List<OrderEntity> orders = orderService.getUserOrders(userId);
        for (OrderEntity order : orders) {
            orderService.deleteOrder(order.getOrderId());
        }
        System.out.println("BusinessLogic: Deleted " + orders.size() + " orders for user " + userId);
        
        // 3. ユーザー削除
        userEntityManager.delete(userId);
        System.out.println("BusinessLogic: User withdrawn - " + user.getName());
    }
    
    /**
     * アクティブユーザー分析
     */
    public UserAnalysisResult analyzeActiveUsers() {
        // 全ユーザー取得
        List<UserEntity> allUsers = userEntityManager.findAll();
        
        int activeUsers = 0;
        int totalOrders = 0;
        
        for (UserEntity user : allUsers) {
            List<OrderEntity> userOrders = orderService.getUserOrders(user.getId());
            if (!userOrders.isEmpty()) {
                activeUsers++;
                totalOrders += userOrders.size();
            }
        }
        
        UserAnalysisResult result = new UserAnalysisResult();
        result.totalUsers = allUsers.size();
        result.activeUsers = activeUsers;
        result.totalOrders = totalOrders;
        result.analysisDate = new Date();
        
        System.out.println("BusinessLogic: Analysis completed - " + activeUsers + "/" + allUsers.size() + " active users");
        
        return result;
    }
    
    /**
     * 重複ユーザーのマージ処理
     */
    public UserEntity mergeUsers(Long primaryUserId, Long secondaryUserId) {
        // 1. 両ユーザー取得
        UserEntity primaryUser = userEntityManager.find(primaryUserId);
        UserEntity secondaryUser = userEntityManager.find(secondaryUserId);
        
        if (primaryUser == null || secondaryUser == null) {
            throw new RuntimeException("One or both users not found");
        }
        
        // 2. セカンダリユーザーの注文をプライマリユーザーに移行
        List<OrderEntity> secondaryOrders = orderService.getUserOrders(secondaryUserId);
        for (OrderEntity order : secondaryOrders) {
            // 注文の所有者を変更（実際の実装では更新処理が必要）
            System.out.println("BusinessLogic: Moving order " + order.getOrderId() + " to primary user");
        }
        
        // 3. セカンダリユーザー削除
        userEntityManager.delete(secondaryUserId);
        
        // 4. プライマリユーザー情報更新（必要に応じて）
        primaryUser.setEmail(primaryUser.getEmail()); // 例：メールアドレス統合ロジック
        userEntityManager.update(primaryUser);
        
        System.out.println("BusinessLogic: Users merged - " + secondaryUser.getName() + " → " + primaryUser.getName());
        
        return primaryUser;
    }
    
    /**
     * ユーザー情報の一括更新
     */
    public void updateUsersInBatch(List<Long> userIds, String emailSuffix) {
        for (Long userId : userIds) {
            UserEntity user = userEntityManager.find(userId);
            if (user != null) {
                user.setEmail(user.getEmail() + emailSuffix);
                userEntityManager.update(user);
                System.out.println("BusinessLogic: Updated user " + userId + " email");
            }
        }
        
        System.out.println("BusinessLogic: Batch update completed for " + userIds.size() + " users");
    }
    
    /**
     * 分析結果クラス
     */
    public static class UserAnalysisResult {
        public int totalUsers;
        public int activeUsers;
        public int totalOrders;
        public Date analysisDate;
    }
}