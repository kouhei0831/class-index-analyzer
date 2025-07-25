package com.example.mapper;

import com.example.entity.UserEntity;

public class UserEntityManager {
    
    public void insert(UserEntity user) {
        // Insert logic here
        System.out.println("Inserting user: " + user.getName());
    }
    
    public UserEntity find(Long id) {
        // Find logic here
        System.out.println("Finding user by id: " + id);
        return new UserEntity();
    }
    
    public void update(UserEntity user) {
        // Update logic here
        System.out.println("Updating user: " + user.getName());
    }
    
    public void delete(Long id) {
        // Delete logic here
        System.out.println("Deleting user by id: " + id);
    }
}