import React, { createContext, useContext, useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { useAuth } from './AuthContext';
import { API_URL } from '../services/api';

const SocketContext = createContext();

const SOCKET_URL = API_URL;

export const SocketProvider = ({ children }) => {
  const { token, user } = useAuth();
  const [socket, setSocket] = useState(null);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [unreadNotifications, setUnreadNotifications] = useState([]);

  useEffect(() => {
    if (!token || !user) {
      if (socket) {
        socket.disconnect();
        setSocket(null);
      }
      return;
    }

    // Connect to WebSocket with token auth details
    const newSocket = io(SOCKET_URL, {
      auth: {
        token: `Bearer ${token}`
      },
      transports: ['websocket', 'polling']
    });

    setSocket(newSocket);

    // Socket event listeners
    newSocket.on('connect', () => {
      console.log('SocketIO Connected: ', newSocket.id);
    });

    newSocket.on('online_users_list', (users) => {
      setOnlineUsers(users);
    });

    newSocket.on('user_status_change', (data) => {
      const { user_id, status } = data;
      setOnlineUsers((prev) => {
        if (status === 'online') {
          return prev.includes(user_id) ? prev : [...prev, user_id];
        } else {
          return prev.filter((id) => id !== user_id);
        }
      });
    });

    return () => {
      newSocket.disconnect();
    };
  }, [token, user]);

  const joinChatRoom = (chatId) => {
    if (socket) {
      socket.emit('join_chat', { chat_id: chatId });
    }
  };

  const leaveChatRoom = (chatId) => {
    if (socket) {
      socket.emit('leave_chat', { chat_id: chatId });
    }
  };

  const sendMessage = (chatId, senderId, content) => {
    if (socket) {
      socket.emit('send_message', { chat_id: chatId, sender_id: senderId, content });
    }
  };

  const startTyping = (chatId, userId) => {
    if (socket) {
      socket.emit('typing', { chat_id: chatId, user_id: userId });
    }
  };

  const stopTyping = (chatId, userId) => {
    if (socket) {
      socket.emit('stop_typing', { chat_id: chatId, user_id: userId });
    }
  };

  const markChatAsRead = (chatId, userId) => {
    if (socket) {
      socket.emit('mark_read', { chat_id: chatId, user_id: userId });
    }
  };

  return (
    <SocketContext.Provider value={{
      socket,
      onlineUsers,
      isUserOnline: (userId) => onlineUsers.includes(Number(userId)),
      joinChatRoom,
      leaveChatRoom,
      sendMessage,
      startTyping,
      stopTyping,
      markChatAsRead
    }}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
