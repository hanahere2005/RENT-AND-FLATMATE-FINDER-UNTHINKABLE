import React, { useEffect, useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../context/SocketContext';
import { useToast } from '../context/ToastContext';
import { Send, Smile, Loader2, MessageSquare, ShieldCheck, CheckCheck } from 'lucide-react';
import api from '../services/api';
import LoadingSkeleton from '../components/LoadingSkeleton';

const ChatPage = () => {
  const { user } = useAuth();
  const { 
    socket, isUserOnline, joinChatRoom, leaveChatRoom, 
    sendMessage, startTyping, stopTyping, markChatAsRead 
  } = useSocket();
  const { showToast } = useToast();

  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loadingChats, setLoadingChats] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);

  // Typing status states
  const [isRecipientTyping, setIsRecipientTyping] = useState(false);
  
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Scroll to bottom on message list update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isRecipientTyping]);

  // Fetch active chats list
  const fetchChats = async () => {
    try {
      const res = await api.get('/chat/list');
      setChats(res.data || []);
    } catch (err) {
      console.error(err);
      showToast("Failed to load conversation threads", "error");
    } fill: {
      setLoadingChats(false);
    }
  };

  useEffect(() => {
    fetchChats();
  }, []);

  // Fetch history when active chat changes
  useEffect(() => {
    if (!activeChat) return;

    const fetchHistory = async () => {
      setLoadingMessages(true);
      try {
        const res = await api.get(`/chat/history/${activeChat.id}`);
        setMessages(res.data || []);
        
        // Join socket room
        joinChatRoom(activeChat.id);
        
        // Mark as read in socket and state
        markChatAsRead(activeChat.id, user?.id);
        setChats(prev => prev.map(c => c.id === activeChat.id ? { ...c, unread_count: 0 } : c));
      } catch (err) {
        console.error(err);
        showToast("Failed to load message history", "error");
      } finally {
        setLoadingMessages(false);
      }
    };

    fetchHistory();

    // Leave room on cleanup
    return () => {
      leaveChatRoom(activeChat.id);
      setIsRecipientTyping(false);
    };
  }, [activeChat]);

  // Listen to live socket events
  useEffect(() => {
    if (!socket) return;

    socket.on('receive_message', (message) => {
      // If message is for the active chat, append it
      if (activeChat && message.chat_id === activeChat.id) {
        setMessages((prev) => [...prev, message]);
        // Auto-mark as read
        if (message.sender_id !== user?.id) {
          markChatAsRead(activeChat.id, user?.id);
        }
      } else {
        // Increment unread count in chats list
        setChats(prev => prev.map(c => c.id === message.chat_id ? { ...c, unread_count: c.unread_count + 1, last_message: message } : c));
      }
    });

    socket.on('user_typing', (data) => {
      if (activeChat && data.chat_id === activeChat.id && data.user_id !== user?.id) {
        setIsRecipientTyping(data.is_typing);
      }
    });

    socket.on('messages_marked_read', (data) => {
      if (activeChat && data.chat_id === activeChat.id && data.reader_id !== user?.id) {
        // Mark all our sent messages in state as read
        setMessages(prev => prev.map(m => m.sender_id === user?.id ? { ...m, is_read: true } : m));
      }
    });

    return () => {
      socket.off('receive_message');
      socket.off('user_typing');
      socket.off('messages_marked_read');
    };
  }, [socket, activeChat, user]);

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    if (!activeChat) return;

    // Trigger typing event
    startTyping(activeChat.id, user?.id);

    // Debounce stop typing
    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      stopTyping(activeChat.id, user?.id);
    }, 2000);
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeChat) return;

    // Send through WebSocket (saves in DB and broadcasts in backend)
    sendMessage(activeChat.id, user?.id, newMessage.trim());
    
    // Stop typing immediately
    stopTyping(activeChat.id, user?.id);
    setNewMessage('');
  };

  if (loadingChats) {
    return <LoadingSkeleton type="chat" />;
  }

  return (
    <div className="flex bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-3xl overflow-hidden shadow-2xl h-[78vh] animate-fade-in">
      
      {/* Sidebar Chat List */}
      <div className={`w-full md:w-80 border-r border-slate-100 dark:border-slate-700/50 flex flex-col justify-between
        ${activeChat ? 'hidden md:flex' : 'flex'}`}>
        
        <div className="p-4 border-b border-slate-100 dark:border-slate-700/50">
          <h2 className="font-extrabold text-base text-slate-900 dark:text-white">Conversations</h2>
          <p className="text-[10px] text-slate-400 font-bold uppercase">Active flatmate connections</p>
        </div>

        <div className="flex-grow overflow-y-auto divide-y divide-slate-50 dark:divide-slate-700/30">
          {chats.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400 space-y-2">
              <MessageSquare className="mx-auto text-slate-300" size={24} />
              <p>No active chats yet. Express interest in properties to start messaging.</p>
            </div>
          ) : (
            chats.map((chat) => {
              const otherUser = chat.other_user;
              const onlineStatus = isUserOnline(otherUser?.id);
              const isActive = activeChat?.id === chat.id;
              
              return (
                <button
                  key={chat.id}
                  onClick={() => setActiveChat(chat)}
                  className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-colors hover:bg-slate-50 dark:hover:bg-slate-700/30
                    ${isActive ? 'bg-blue-50/50 dark:bg-slate-700/20' : ''}`}
                >
                  {/* Profile avatar with online indicator dot */}
                  <div className="relative flex-shrink-0">
                    <div className="w-11 h-11 rounded-full bg-blue-100 dark:bg-slate-900 flex items-center justify-center font-black text-sm text-blue-600 dark:text-blue-400">
                      {otherUser?.email.substring(0, 2).toUpperCase()}
                    </div>
                    {onlineStatus && (
                      <span className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-800 animate-pulse"></span>
                    )}
                  </div>

                  {/* Message previews */}
                  <div className="flex-grow min-w-0">
                    <div className="flex justify-between items-baseline mb-0.5">
                      <span className="font-bold text-xs text-slate-900 dark:text-white truncate">
                        {otherUser?.email}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 dark:text-slate-400 truncate">
                      {chat.last_message ? chat.last_message.content : "Start chatting now..."}
                    </p>
                  </div>

                  {/* Unread badge count */}
                  {chat.unread_count > 0 && (
                    <span className="flex-shrink-0 bg-blue-600 text-white rounded-full w-5 h-5 font-black text-[9px] flex items-center justify-center">
                      {chat.unread_count}
                    </span>
                  )}

                </button>
              );
            })
          )}
        </div>

      </div>

      {/* Main Conversation Window */}
      <div className={`flex-grow flex flex-col justify-between bg-slate-50/50 dark:bg-slate-900/10
        ${!activeChat ? 'hidden md:flex items-center justify-center p-8' : 'flex'}`}>
        
        {activeChat ? (
          <>
            {/* Thread Header */}
            <div className="bg-white dark:bg-slate-800 px-6 py-3 border-b border-slate-100 dark:border-slate-700/50 flex items-center gap-3">
              <button 
                onClick={() => setActiveChat(null)}
                className="md:hidden text-blue-600 font-bold text-xs"
              >
                Back
              </button>
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-slate-900 flex items-center justify-center font-bold text-xs text-blue-600 dark:text-blue-400">
                  {activeChat.other_user?.email.substring(0, 2).toUpperCase()}
                </div>
                {isUserOnline(activeChat.other_user?.id) && (
                  <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-800"></span>
                )}
              </div>
              <div>
                <h3 className="font-extrabold text-sm text-slate-900 dark:text-white leading-tight">
                  {activeChat.other_user?.email}
                </h3>
                <span className="text-[9px] font-bold uppercase text-slate-400">
                  {isUserOnline(activeChat.other_user?.id) ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>

            {/* Message Thread Scroll panel */}
            <div className="flex-grow overflow-y-auto p-6 space-y-4">
              {loadingMessages ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="animate-spin text-blue-600" size={24} />
                </div>
              ) : (
                messages.map((msg) => {
                  const isMine = msg.sender_id === user?.id;
                  
                  return (
                    <div 
                      key={msg.id} 
                      className={`flex flex-col gap-1 ${isMine ? 'items-end' : 'items-start'}`}
                    >
                      <div className={`max-w-[70%] p-3.5 rounded-2xl shadow-sm text-xs font-semibold leading-relaxed
                        ${isMine 
                          ? 'bg-blue-600 text-white rounded-br-none' 
                          : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-bl-none border border-slate-100 dark:border-slate-700/50'}`}>
                        {msg.content}
                      </div>
                      
                      {/* Timestamp & read receipts */}
                      <div className="flex items-center gap-1.5 px-1">
                        <span className="text-[9px] text-slate-400">
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {isMine && (
                          <span>
                            <CheckCheck size={12} className={msg.is_read ? 'text-blue-500' : 'text-slate-300'} />
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}

              {/* Live typing status indicators */}
              {isRecipientTyping && (
                <div className="flex items-center gap-2">
                  <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 py-2.5 px-4 rounded-2xl rounded-bl-none shadow-sm flex gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce delay-150"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce delay-300"></span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form Footer */}
            <form onSubmit={handleSend} className="bg-white dark:bg-slate-800 px-6 py-4 border-t border-slate-100 dark:border-slate-700/50 flex gap-2">
              <input
                type="text"
                placeholder="Type a message..."
                value={newMessage}
                onChange={handleInputChange}
                className="flex-grow px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
              <button
                type="submit"
                disabled={!newMessage.trim()}
                className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold transition-all shadow"
              >
                <Send size={16} />
              </button>
            </form>
          </>
        ) : (
          <div className="text-center space-y-3">
            <MessageSquare size={48} className="mx-auto text-slate-300 dark:text-slate-600" />
            <h3 className="font-extrabold text-base">Select a conversation</h3>
            <p className="text-xs text-slate-400 max-w-xs font-medium">Click on an active roommate connection in the left sidebar to exchange instant messages.</p>
          </div>
        )}

      </div>

    </div>
  );
};

export default ChatPage;
