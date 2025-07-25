package com.example.service;

import com.example.entity.OrderEntity;
import com.example.entity.UserEntity;
import com.example.ormapper.OrderORMapper;
import com.example.mapper.UserEntityManager;
import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

/**
 * 注文サービス
 * UserServiceとは異なり、直接ORMapperを使用するパターン
 */
public class OrderService {
    
    private OrderORMapper orderORMapper;
    private UserEntityManager userEntityManager;
    
    public OrderService() {
        this.orderORMapper = new OrderORMapper();
        this.userEntityManager = new UserEntityManager();
    }
    
    /**
     * 新規注文作成
     */
    public OrderEntity createOrder(Long userId, String productName, Integer quantity, BigDecimal price) {
        // ユーザー存在チェック
        UserEntity user = userEntityManager.find(userId);
        if (user == null) {
            throw new RuntimeException("User not found: " + userId);
        }
        
        OrderEntity order = new OrderEntity();
        order.setUserId(userId);
        order.setProductName(productName);
        order.setQuantity(quantity);
        order.setPrice(price);
        order.setOrderDate(new Date());
        order.setStatus("PENDING");
        
        orderORMapper.doInsert(order);
        System.out.println("OrderService: Order created for user " + userId);
        
        return order;
    }
    
    /**
     * 注文検索
     */
    public OrderEntity findOrderById(Long orderId) {
        return orderORMapper.select(orderId);
    }
    
    /**
     * ユーザーの注文履歴取得
     */
    public List<OrderEntity> getUserOrders(Long userId) {
        return orderORMapper.selectByUserId(userId);
    }
    
    /**
     * 注文ステータス更新
     */
    public void updateOrderStatus(Long orderId, String status) {
        if (!orderORMapper.exists(orderId)) {
            throw new RuntimeException("Order not found: " + orderId);
        }
        
        OrderEntity order = orderORMapper.select(orderId);
        order.setStatus(status);
        
        orderORMapper.doUpdate(order);
        System.out.println("OrderService: Order status updated to " + status);
    }
    
    /**
     * 注文キャンセル
     */
    public void cancelOrder(Long orderId) {
        updateOrderStatus(orderId, "CANCELLED");
    }
    
    /**
     * 注文削除
     */
    public void deleteOrder(Long orderId) {
        orderORMapper.doDelete(orderId);
        System.out.println("OrderService: Order deleted " + orderId);
    }
}