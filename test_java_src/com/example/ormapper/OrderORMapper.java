package com.example.ormapper;

import com.example.entity.OrderEntity;
import java.util.List;

/**
 * Order Entity OR Mapper
 */
public class OrderORMapper {
    
    /**
     * 注文挿入
     */
    public void doInsert(OrderEntity order) {
        System.out.println("SQL: INSERT INTO orders (user_id, product_name, quantity, price) VALUES (" 
            + order.getUserId() + ", '" + order.getProductName() + "', " + order.getQuantity() + ", " + order.getPrice() + ")");
    }
    
    /**
     * 注文検索（ID指定）
     */
    public OrderEntity select(Long orderId) {
        System.out.println("SQL: SELECT * FROM orders WHERE order_id = " + orderId);
        return new OrderEntity();
    }
    
    /**
     * ユーザーの注文一覧取得
     */
    public List<OrderEntity> selectByUserId(Long userId) {
        System.out.println("SQL: SELECT * FROM orders WHERE user_id = " + userId);
        return List.of(new OrderEntity());
    }
    
    /**
     * 注文ステータス更新
     */
    public void doUpdate(OrderEntity order) {
        System.out.println("SQL: UPDATE orders SET status = '" + order.getStatus() + "' WHERE order_id = " + order.getOrderId());
    }
    
    /**
     * 注文削除
     */
    public void doDelete(Long orderId) {
        System.out.println("SQL: DELETE FROM orders WHERE order_id = " + orderId);
    }
    
    /**
     * 注文存在チェック
     */
    public boolean exists(Long orderId) {
        System.out.println("SQL: SELECT COUNT(*) FROM orders WHERE order_id = " + orderId);
        return true;
    }
}