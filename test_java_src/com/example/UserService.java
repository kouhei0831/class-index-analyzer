package com.example;

import com.example.entity.UserEntity;
import com.example.mapper.UserEntityManager;

public class UserService {
    
    private UserEntityManager userManager;
    
    public UserService() {
        this.userManager = new UserEntityManager();
    }
    
    public void createUser(String name, String email) {
        UserEntity user = new UserEntity();
        user.setName(name);
        user.setEmail(email);
        userManager.insert(user);
    }
    
    public UserEntity findUserById(Long id) {
        return userManager.find(id);
    }
    
    public void updateUser(UserEntity user) {
        userManager.update(user);
    }
    
    public void deleteUser(Long id) {
        userManager.delete(id);
    }
}