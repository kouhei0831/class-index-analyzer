package com.example.controller;

import com.example.entity.OrderEntity;
import com.example.entity.UserEntity;
import com.example.mapper.UserEntityManager;
import com.example.service.OrderService;
import java.math.BigDecimal;
import java.util.List;

/**
 * Order Controller
 * 注文管理API - 複数のEntityとEntityManagerをimport
 */
public class OrderController {
    
    private OrderService orderService;
    private UserEntityManager userEntityManager;
    
    public OrderController() {
        this.orderService = new OrderService();
        this.userEntityManager = new UserEntityManager();
    }
    
    /**
     * 注文作成API
     * POST /api/orders
     */
    public OrderEntity createOrder(Long userId, String productName, Integer quantity, BigDecimal price) {
        // ユーザー存在確認（EntityManagerで直接チェック）
        UserEntity user = userEntityManager.find(userId);
        if (user == null) {
            throw new RuntimeException("User not found: " + userId);
        }
        
        // 注文作成（Serviceレイヤー経由）
        OrderEntity order = orderService.createOrder(userId, productName, quantity, price);
        
        System.out.println("OrderController: Order created for user " + user.getName());
        return order;
    }
    
    /**
     * 注文取得API
     * GET /api/orders/{orderId}
     */
    public OrderEntity getOrder(Long orderId) {
        return orderService.findOrderById(orderId);
    }
    
    /**
     * ユーザーの注文一覧API
     * GET /api/users/{userId}/orders
     */
    public List<OrderEntity> getUserOrders(Long userId) {
        // ユーザー存在確認
        UserEntity user = userEntityManager.find(userId);
        if (user == null) {
            throw new RuntimeException("User not found: " + userId);
        }
        
        return orderService.getUserOrders(userId);
    }
    
    /**
     * 注文ステータス更新API
     * PUT /api/orders/{orderId}/status
     */
    public void updateOrderStatus(Long orderId, String status) {
        orderService.updateOrderStatus(orderId, status);
        System.out.println("OrderController: Order status updated");
    }
    
    /**
     * 注文キャンセルAPI
     * POST /api/orders/{orderId}/cancel
     */
    public void cancelOrder(Long orderId) {
        orderService.cancelOrder(orderId);
        System.out.println("OrderController: Order cancelled");
    }
    
    /**
     * 注文削除API
     * DELETE /api/orders/{orderId}
     */
    public void deleteOrder(Long orderId) {
        orderService.deleteOrder(orderId);
        System.out.println("OrderController: Order deleted");
    }
    
    /**
     * ユーザーの全注文削除API
     * DELETE /api/users/{userId}/orders
     */
    public void deleteAllUserOrders(Long userId) {
        // ユーザー存在確認
        UserEntity user = userEntityManager.find(userId);
        if (user == null) {
            throw new RuntimeException("User not found: " + userId);
        }
        
        List<OrderEntity> orders = orderService.getUserOrders(userId);
        for (OrderEntity order : orders) {
            orderService.deleteOrder(order.getOrderId());
        }
        
        System.out.println("OrderController: All orders deleted for user " + userId);
    }
}